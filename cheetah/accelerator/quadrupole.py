from typing import Literal, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.patches import Rectangle
from scipy.constants import physical_constants
from torch import Size, nn

from cheetah.particles import Beam, ParticleBeam
from cheetah.track_methods import base_rmatrix, misalignment_matrix
from cheetah.utils import UniqueNameGenerator, bmadx

from .element import Element

generate_unique_name = UniqueNameGenerator(prefix="unnamed_element")

electron_mass_eV = torch.tensor(
    physical_constants["electron mass energy equivalent in MeV"][0] * 1e6
)


class Quadrupole(Element):
    """
    Quadrupole magnet in a particle accelerator.

    :param length: Length in meters.
    :param k1: Strength of the quadrupole in 1/m^-2.
    :param misalignment: Misalignment vector of the quadrupole in x- and y-directions.
    :param tilt: Tilt angle of the quadrupole in x-y plane [rad]. pi/4 for
        skew-quadrupole.
    :param num_steps: Number of drift-kick-drift steps to use for tracking through the
        element when tracking method is set to `"bmadx"`.
    :param tracking_method: Method to use for tracking through the element.
    :param name: Unique identifier of the element.
    """

    def __init__(
        self,
        length: Union[torch.Tensor, nn.Parameter],
        k1: Optional[Union[torch.Tensor, nn.Parameter]] = None,
        misalignment: Optional[Union[torch.Tensor, nn.Parameter]] = None,
        tilt: Optional[Union[torch.Tensor, nn.Parameter]] = None,
        num_steps: int = 1,
        tracking_method: Literal["cheetah", "bmadx"] = "cheetah",
        name: Optional[str] = None,
        device=None,
        dtype=torch.float32,
    ) -> None:
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__(name=name)

        self.register_buffer("length", torch.as_tensor(length, **factory_kwargs))
        self.register_buffer(
            "k1",
            (
                torch.as_tensor(k1, **factory_kwargs)
                if k1 is not None
                else torch.zeros_like(self.length)
            ),
        )
        self.register_buffer(
            "misalignment",
            (
                torch.as_tensor(misalignment, **factory_kwargs)
                if misalignment is not None
                else torch.zeros((*self.length.shape, 2), **factory_kwargs)
            ),
        )
        self.register_buffer(
            "tilt",
            (
                torch.as_tensor(tilt, **factory_kwargs)
                if tilt is not None
                else torch.zeros_like(self.length)
            ),
        )
        self.num_steps = num_steps
        self.tracking_method = tracking_method

    def transfer_map(self, energy: torch.Tensor) -> torch.Tensor:
        R = base_rmatrix(
            length=self.length,
            k1=self.k1,
            hx=torch.zeros_like(self.length),
            tilt=self.tilt,
            energy=energy,
        )

        if torch.all(self.misalignment == 0):
            return R
        else:
            R_entry, R_exit = misalignment_matrix(self.misalignment)
            R = torch.einsum("...ij,...jk,...kl->...il", R_exit, R, R_entry)
            return R

    def track(self, incoming: Beam) -> Beam:
        """
        Track particles through the quadrupole element.

        :param incoming: Beam entering the element.
        :return: Beam exiting the element.
        """
        if self.tracking_method == "cheetah":
            return super().track(incoming)
        elif self.tracking_method == "bmadx":
            assert isinstance(
                incoming, ParticleBeam
            ), "Bmad-X tracking is currently only supported for `ParticleBeam`."
            return self._track_bmadx(incoming)
        else:
            raise ValueError(
                f"Invalid tracking method {self.tracking_method}. "
                + "Supported methods are 'cheetah' and 'bmadx'."
            )

    def _track_bmadx(self, incoming: ParticleBeam) -> ParticleBeam:
        """
        Track particles through the quadrupole element using the Bmad-X tracking method.

        :param incoming: Beam entering the element. Currently only supports
            `ParticleBeam`.
        :return: Beam exiting the element.
        """
        # Compute Bmad coordinates and p0c
        mc2 = electron_mass_eV.to(
            device=incoming.particles.device, dtype=incoming.particles.dtype
        )
        bmad_coords, p0c = bmadx.cheetah_to_bmad_coords(
            incoming.particles, incoming.energy, mc2
        )
        x = bmad_coords[..., 0]
        px = bmad_coords[..., 1]
        y = bmad_coords[..., 2]
        py = bmad_coords[..., 3]
        z = bmad_coords[..., 4]
        pz = bmad_coords[..., 5]

        x_offset = self.misalignment[..., 0]
        y_offset = self.misalignment[..., 1]

        step_length = self.length / self.num_steps
        b1 = self.k1 * self.length

        # Begin Bmad-X tracking
        x, px, y, py = bmadx.offset_particle_set(
            x_offset, y_offset, self.tilt, x, px, y, py
        )

        for _ in range(self.num_steps):
            rel_p = 1 + pz  # Particle's relative momentum (P/P0)
            k1 = b1.unsqueeze(-1) / (self.length.unsqueeze(-1) * rel_p)

            tx, dzx = bmadx.calculate_quadrupole_coefficients(-k1, step_length, rel_p)
            ty, dzy = bmadx.calculate_quadrupole_coefficients(k1, step_length, rel_p)

            z = (
                z
                + dzx[0] * x**2
                + dzx[1] * x * px
                + dzx[2] * px**2
                + dzy[0] * y**2
                + dzy[1] * y * py
                + dzy[2] * py**2
            )

            x_next = tx[0][0] * x + tx[0][1] * px
            px_next = tx[1][0] * x + tx[1][1] * px
            y_next = ty[0][0] * y + ty[0][1] * py
            py_next = ty[1][0] * y + ty[1][1] * py

            x, px, y, py = x_next, px_next, y_next, py_next

            z = z + bmadx.low_energy_z_correction(pz, p0c, mc2, step_length)

        # s = s + l
        x, px, y, py = bmadx.offset_particle_unset(
            x_offset, y_offset, self.tilt, x, px, y, py
        )

        # End of Bmad-X tracking
        bmad_coords[..., 0] = x
        bmad_coords[..., 1] = px
        bmad_coords[..., 2] = y
        bmad_coords[..., 3] = py
        bmad_coords[..., 4] = z
        bmad_coords[..., 5] = pz

        # Convert back to Cheetah coordinates
        cheetah_coords, ref_energy = bmadx.bmad_to_cheetah_coords(bmad_coords, p0c, mc2)

        outgoing_beam = ParticleBeam(
            cheetah_coords,
            ref_energy,
            particle_charges=incoming.particle_charges,
            device=incoming.particles.device,
            dtype=incoming.particles.dtype,
        )
        return outgoing_beam

    def broadcast(self, shape: Size) -> Element:
        return self.__class__(
            length=self.length.repeat(shape),
            k1=self.k1.repeat(shape),
            misalignment=self.misalignment.repeat((*shape, 1)),
            tilt=self.tilt.repeat(shape),
            name=self.name,
            device=self.length.device,
            dtype=self.length.dtype,
        )

    @property
    def is_skippable(self) -> bool:
        return self.tracking_method == "cheetah"

    @property
    def is_active(self) -> bool:
        return any(self.k1 != 0)

    def split(self, resolution: torch.Tensor) -> list[Element]:
        num_splits = torch.ceil(torch.max(self.length) / resolution).int()
        return [
            Quadrupole(
                self.length / num_splits,
                self.k1,
                misalignment=self.misalignment,
                tilt=self.tilt,
                num_steps=self.num_steps,
                tracking_method=self.tracking_method,
                dtype=self.length.dtype,
                device=self.length.device,
            )
            for i in range(num_splits)
        ]

    def plot(self, ax: plt.Axes, s: float) -> None:
        alpha = 1 if self.is_active else 0.2
        height = 0.8 * (np.sign(self.k1[0]) if self.is_active else 1)
        patch = Rectangle(
            (s, 0), self.length[0], height, color="tab:red", alpha=alpha, zorder=2
        )
        ax.add_patch(patch)

    @property
    def defining_features(self) -> list[str]:
        return super().defining_features + ["length", "k1", "misalignment", "tilt"]

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(length={repr(self.length)}, "
            + f"k1={repr(self.k1)}, "
            + f"misalignment={repr(self.misalignment)}, "
            + f"tilt={repr(self.tilt)}, "
            + f"num_steps={repr(self.num_steps)}, "
            + f"tracking_method={repr(self.tracking_method)}, "
            + f"name={repr(self.name)})"
        )
