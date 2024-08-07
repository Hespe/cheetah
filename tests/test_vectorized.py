import torch

import cheetah

from .resources import ARESlatticeStage3v1_9 as ares


def test_segment_length_shape():
    """Test that the shape of a segment's length matches the input."""
    segment = cheetah.Segment(
        elements=[
            cheetah.Drift(length=torch.tensor([0.6, 0.5])),
            cheetah.Quadrupole(
                length=torch.tensor([0.2, 0.25]), k1=torch.tensor([4.2, 4.2])
            ),
            cheetah.Drift(length=torch.tensor([0.4, 0.3])),
        ]
    )

    assert segment.length.shape == (2,)


def test_segment_length_shape_2d():
    """
    Test that the shape of a segment's length matches the input for a batch with
    multiple dimensions.
    """
    segment = cheetah.Segment(
        elements=[
            cheetah.Drift(length=torch.tensor([[0.6, 0.5], [0.4, 0.3], [0.4, 0.3]])),
            cheetah.Quadrupole(
                length=torch.tensor([[0.2, 0.25], [0.3, 0.35], [0.3, 0.35]]),
                k1=torch.tensor([[4.2, 4.2], [4.3, 4.3], [4.3, 4.3]]),
            ),
            cheetah.Drift(length=torch.tensor([[0.4, 0.3], [0.2, 0.1], [0.2, 0.1]])),
        ]
    )

    assert segment.length.shape == (3, 2)


def test_track_particle_single_element_shape():
    """
    Test that the shape of a beam tracked through a single element matches the input.
    """
    quadrupole = cheetah.Quadrupole(
        length=torch.tensor([0.2, 0.25]), k1=torch.tensor([4.2, 4.2])
    )
    incoming = cheetah.ParticleBeam.from_parameters(
        num_particles=100_000, sigma_x=torch.tensor([1e-5, 2e-5])
    )

    outgoing = quadrupole.track(incoming)

    assert outgoing.particles.shape == incoming.particles.shape
    assert outgoing.particles.shape == (2, 100_000, 7)
    assert outgoing.mu_x.shape == (2,)
    assert outgoing.mu_px.shape == (2,)
    assert outgoing.mu_y.shape == (2,)
    assert outgoing.mu_py.shape == (2,)
    assert outgoing.sigma_x.shape == (2,)
    assert outgoing.sigma_px.shape == (2,)
    assert outgoing.sigma_y.shape == (2,)
    assert outgoing.sigma_py.shape == (2,)
    assert outgoing.sigma_tau.shape == (2,)
    assert outgoing.sigma_p.shape == (2,)
    assert outgoing.energy.shape == (2,)
    assert outgoing.total_charge.shape == (2,)
    assert outgoing.particle_charges.shape == (2, 100_000)
    assert isinstance(outgoing.num_particles, int)


def test_track_particle_single_element_shape_2d():
    """
    Test that the shape of a beam tracked through a single element matches the input for
    an n-dimensional batch.
    """
    quadrupole = cheetah.Quadrupole(
        length=torch.tensor([[0.2, 0.25], [0.3, 0.35], [0.4, 0.45]]),
        k1=torch.tensor([[4.2, 4.2], [4.3, 4.3], [4.4, 4.4]]),
    )
    incoming = cheetah.ParticleBeam.from_parameters(
        num_particles=100_000,
        sigma_x=torch.tensor([[1e-5, 2e-5], [2e-5, 3e-5], [3e-5, 4e-5]]),
    )

    outgoing = quadrupole.track(incoming)

    assert outgoing.particles.shape == incoming.particles.shape
    assert outgoing.particles.shape == (3, 2, 100_000, 7)
    assert outgoing.mu_x.shape == (3, 2)
    assert outgoing.mu_px.shape == (3, 2)
    assert outgoing.mu_y.shape == (3, 2)
    assert outgoing.mu_py.shape == (3, 2)
    assert outgoing.sigma_x.shape == (3, 2)
    assert outgoing.sigma_px.shape == (3, 2)
    assert outgoing.sigma_y.shape == (3, 2)
    assert outgoing.sigma_py.shape == (3, 2)
    assert outgoing.sigma_tau.shape == (3, 2)
    assert outgoing.sigma_p.shape == (3, 2)
    assert outgoing.energy.shape == (3, 2)
    assert outgoing.total_charge.shape == (3, 2)
    assert outgoing.particle_charges.shape == (3, 2, 100_000)
    assert isinstance(outgoing.num_particles, int)


def test_track_particle_segment_shape():
    """
    Test that the shape of a beam tracked through a segment matches the input.
    """
    segment = cheetah.Segment(
        elements=[
            cheetah.Drift(length=torch.tensor([0.6, 0.5])),
            cheetah.Quadrupole(
                length=torch.tensor([0.2, 0.25]), k1=torch.tensor([4.2, 4.2])
            ),
            cheetah.Drift(length=torch.tensor([0.4, 0.3])),
        ]
    )
    incoming = cheetah.ParticleBeam.from_parameters(
        num_particles=100_000, sigma_x=torch.tensor([1e-5, 2e-5])
    )

    outgoing = segment.track(incoming)

    assert outgoing.particles.shape == incoming.particles.shape
    assert outgoing.particles.shape == (2, 100_000, 7)
    assert outgoing.mu_x.shape == (2,)
    assert outgoing.mu_px.shape == (2,)
    assert outgoing.mu_y.shape == (2,)
    assert outgoing.mu_py.shape == (2,)
    assert outgoing.sigma_x.shape == (2,)
    assert outgoing.sigma_px.shape == (2,)
    assert outgoing.sigma_y.shape == (2,)
    assert outgoing.sigma_py.shape == (2,)
    assert outgoing.sigma_tau.shape == (2,)
    assert outgoing.sigma_p.shape == (2,)
    assert outgoing.energy.shape == (2,)
    assert outgoing.total_charge.shape == (2,)
    assert outgoing.particle_charges.shape == (2, 100_000)
    assert isinstance(outgoing.num_particles, int)


def test_track_particle_segment_shape_2d():
    """
    Test that the shape of a beam tracked through a segment matches the input for the
    case of a multi-dimensional batch.
    """
    segment = cheetah.Segment(
        elements=[
            cheetah.Drift(length=torch.tensor([[0.6, 0.5], [0.4, 0.3], [0.2, 0.1]])),
            cheetah.Quadrupole(
                length=torch.tensor([[0.2, 0.25], [0.3, 0.35], [0.4, 0.45]]),
                k1=torch.tensor([[4.2, 4.2], [4.3, 4.3], [4.4, 4.4]]),
            ),
            cheetah.Drift(length=torch.tensor([[0.4, 0.3], [0.6, 0.5], [0.8, 0.7]])),
        ]
    )
    incoming = cheetah.ParticleBeam.from_parameters(
        num_particles=100_000,
        sigma_x=torch.tensor([[1e-5, 2e-5], [2e-5, 3e-5], [3e-5, 4e-5]]),
    )

    outgoing = segment.track(incoming)

    assert outgoing.particles.shape == incoming.particles.shape
    assert outgoing.particles.shape == (3, 2, 100_000, 7)
    assert outgoing.mu_x.shape == (3, 2)
    assert outgoing.mu_px.shape == (3, 2)
    assert outgoing.mu_y.shape == (3, 2)
    assert outgoing.mu_py.shape == (3, 2)
    assert outgoing.sigma_x.shape == (3, 2)
    assert outgoing.sigma_px.shape == (3, 2)
    assert outgoing.sigma_y.shape == (3, 2)
    assert outgoing.sigma_py.shape == (3, 2)
    assert outgoing.sigma_tau.shape == (3, 2)
    assert outgoing.sigma_p.shape == (3, 2)
    assert outgoing.energy.shape == (3, 2)
    assert outgoing.total_charge.shape == (3, 2)
    assert outgoing.particle_charges.shape == (3, 2, 100_000)
    assert isinstance(outgoing.num_particles, int)


def test_track_parameter_single_element_shape():
    """
    Test that the shape of a beam tracked through a single element matches the input.
    """
    quadrupole = cheetah.Quadrupole(
        length=torch.tensor([0.2, 0.25]), k1=torch.tensor([4.2, 4.2])
    )
    incoming = cheetah.ParameterBeam.from_parameters(sigma_x=torch.tensor([1e-5, 2e-5]))

    outgoing = quadrupole.track(incoming)

    assert outgoing.mu_x.shape == (2,)
    assert outgoing.mu_px.shape == (2,)
    assert outgoing.mu_y.shape == (2,)
    assert outgoing.mu_py.shape == (2,)
    assert outgoing.sigma_x.shape == (2,)
    assert outgoing.sigma_px.shape == (2,)
    assert outgoing.sigma_y.shape == (2,)
    assert outgoing.sigma_py.shape == (2,)
    assert outgoing.sigma_tau.shape == (2,)
    assert outgoing.sigma_p.shape == (2,)
    assert outgoing.energy.shape == (2,)
    assert outgoing.total_charge.shape == (2,)


def test_track_parameter_single_element_shape_2d():
    """
    Test that the shape of a beam tracked through a single element matches the input for
    an n-dimensional batch.
    """
    quadrupole = cheetah.Quadrupole(
        length=torch.tensor([[0.2, 0.25], [0.3, 0.35], [0.4, 0.45]]),
        k1=torch.tensor([[4.2, 4.2], [4.3, 4.3], [4.4, 4.4]]),
    )
    incoming = cheetah.ParameterBeam.from_parameters(
        sigma_x=torch.tensor([[1e-5, 2e-5], [2e-5, 3e-5], [3e-5, 4e-5]])
    )

    outgoing = quadrupole.track(incoming)

    assert outgoing.mu_x.shape == (3, 2)
    assert outgoing.mu_px.shape == (3, 2)
    assert outgoing.mu_y.shape == (3, 2)
    assert outgoing.mu_py.shape == (3, 2)
    assert outgoing.sigma_x.shape == (3, 2)
    assert outgoing.sigma_px.shape == (3, 2)
    assert outgoing.sigma_y.shape == (3, 2)
    assert outgoing.sigma_py.shape == (3, 2)
    assert outgoing.sigma_tau.shape == (3, 2)
    assert outgoing.sigma_p.shape == (3, 2)
    assert outgoing.energy.shape == (3, 2)
    assert outgoing.total_charge.shape == (3, 2)


def test_track_parameter_segment_shape():
    """
    Test that the shape of a beam tracked through a segment matches the input.
    """
    segment = cheetah.Segment(
        elements=[
            cheetah.Drift(length=torch.tensor([0.6, 0.5])),
            cheetah.Quadrupole(
                length=torch.tensor([0.2, 0.25]), k1=torch.tensor([4.2, 4.2])
            ),
            cheetah.Drift(length=torch.tensor([0.4, 0.3])),
        ]
    )
    incoming = cheetah.ParameterBeam.from_parameters(sigma_x=torch.tensor([1e-5, 2e-5]))

    outgoing = segment.track(incoming)

    assert outgoing.mu_x.shape == (2,)
    assert outgoing.mu_px.shape == (2,)
    assert outgoing.mu_y.shape == (2,)
    assert outgoing.mu_py.shape == (2,)
    assert outgoing.sigma_x.shape == (2,)
    assert outgoing.sigma_px.shape == (2,)
    assert outgoing.sigma_y.shape == (2,)
    assert outgoing.sigma_py.shape == (2,)
    assert outgoing.sigma_tau.shape == (2,)
    assert outgoing.sigma_p.shape == (2,)
    assert outgoing.energy.shape == (2,)
    assert outgoing.total_charge.shape == (2,)


def test_track_parameter_segment_shape_2d():
    """
    Test that the shape of a beam tracked through a segment matches the input for the
    case of a multi-dimensional batch.
    """
    segment = cheetah.Segment(
        elements=[
            cheetah.Drift(length=torch.tensor([[0.6, 0.5], [0.4, 0.3], [0.2, 0.1]])),
            cheetah.Quadrupole(
                length=torch.tensor([[0.2, 0.25], [0.3, 0.35], [0.4, 0.45]]),
                k1=torch.tensor([[4.2, 4.2], [4.3, 4.3], [4.4, 4.4]]),
            ),
            cheetah.Drift(length=torch.tensor([[0.4, 0.3], [0.6, 0.5], [0.8, 0.7]])),
        ]
    )
    incoming = cheetah.ParameterBeam.from_parameters(
        sigma_x=torch.tensor([[1e-5, 2e-5], [2e-5, 3e-5], [3e-5, 4e-5]])
    )

    outgoing = segment.track(incoming)

    assert outgoing.mu_x.shape == (3, 2)
    assert outgoing.mu_px.shape == (3, 2)
    assert outgoing.mu_y.shape == (3, 2)
    assert outgoing.mu_py.shape == (3, 2)
    assert outgoing.sigma_x.shape == (3, 2)
    assert outgoing.sigma_px.shape == (3, 2)
    assert outgoing.sigma_y.shape == (3, 2)
    assert outgoing.sigma_py.shape == (3, 2)
    assert outgoing.sigma_tau.shape == (3, 2)
    assert outgoing.sigma_p.shape == (3, 2)
    assert outgoing.energy.shape == (3, 2)
    assert outgoing.total_charge.shape == (3, 2)


def test_enormous_through_ares():
    """Test ARES EA with a huge number of settings."""
    segment = cheetah.Segment.from_ocelot(ares.cell).subcell("AREASOLA1", "AREABSCR1")
    incoming = cheetah.ParameterBeam.from_astra(
        "tests/resources/ACHIP_EA1_2021.1351.001"
    )

    segment_broadcast = segment.broadcast((3, 100_000))
    incoming_broadcast = incoming.broadcast((3, 100_000))

    segment_broadcast.AREAMQZM1.k1 = torch.linspace(-30.0, 30.0, 100_000).repeat(3, 1)

    outgoing = segment_broadcast.track(incoming_broadcast)

    assert outgoing.mu_x.shape == (3, 100_000)
    assert outgoing.mu_px.shape == (3, 100_000)
    assert outgoing.mu_y.shape == (3, 100_000)
    assert outgoing.mu_py.shape == (3, 100_000)
    assert outgoing.sigma_x.shape == (3, 100_000)
    assert outgoing.sigma_px.shape == (3, 100_000)
    assert outgoing.sigma_y.shape == (3, 100_000)
    assert outgoing.sigma_py.shape == (3, 100_000)
    assert outgoing.sigma_tau.shape == (3, 100_000)
    assert outgoing.sigma_p.shape == (3, 100_000)
    assert outgoing.energy.shape == (3, 100_000)
    assert outgoing.total_charge.shape == (3, 100_000)


def test_before_after_broadcast_tracking_equal_cavity():
    """
    Test that when tracking through a segment after broadcasting, the resulting beam is
    the same as in the segment before broadcasting. A cavity is used as a reference.
    """
    cavity = cheetah.Cavity(
        length=torch.tensor([3.0441]),
        voltage=torch.tensor([48198468.0]),
        phase=torch.tensor([-0.0]),
        frequency=torch.tensor([2.8560e09]),
        name="k26_2d",
    )
    incoming = cheetah.ParameterBeam.from_astra(
        "tests/resources/ACHIP_EA1_2021.1351.001"
    )
    outgoing = cavity.track(incoming)

    broadcast_cavity = cavity.broadcast((3, 10))
    broadcast_incoming = incoming.broadcast((3, 10))
    broadcast_outgoing = broadcast_cavity.track(broadcast_incoming)

    for i in range(3):
        for j in range(10):
            assert torch.all(broadcast_outgoing._mu[i, j] == outgoing._mu[0])
            assert torch.all(broadcast_outgoing._cov[i, j] == outgoing._cov[0])


def test_before_after_broadcast_tracking_equal_ares_ea():
    """
    Test that when tracking through a segment after broadcasting, the resulting beam is
    the same as in the segment before broadcasting. The ARES EA is used as a reference.
    """
    segment = cheetah.Segment.from_ocelot(ares.cell).subcell("AREASOLA1", "AREABSCR1")
    incoming = cheetah.ParameterBeam.from_astra(
        "tests/resources/ACHIP_EA1_2021.1351.001"
    )
    segment.AREAMQZM1.k1 = torch.tensor([4.2])
    outgoing = segment.track(incoming)

    broadcast_segment = segment.broadcast((3, 10))
    broadcast_incoming = incoming.broadcast((3, 10))
    broadcast_outgoing = broadcast_segment.track(broadcast_incoming)

    for i in range(3):
        for j in range(10):
            assert torch.allclose(broadcast_outgoing._mu[i, j], outgoing._mu[0])
            assert torch.allclose(broadcast_outgoing._cov[i, j], outgoing._cov[0])


def test_broadcast_customtransfermap():
    """Test that broadcasting a `CustomTransferMap` element gives the correct result."""
    tm = torch.tensor(
        [
            [
                [1.0, 4.0e-02, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0e-05],
                [0.0, 0.0, 1.0, 4.0e-02, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 1.0, -4.6422e-07, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            ]
        ]
    )

    element = cheetah.CustomTransferMap(length=torch.tensor([0.4]), transfer_map=tm)
    broadcast_element = element.broadcast((3, 10))

    assert broadcast_element.length.shape == (3, 10)
    assert broadcast_element._transfer_map.shape == (3, 10, 7, 7)
    for i in range(3):
        for j in range(10):
            assert torch.all(broadcast_element._transfer_map[i, j] == tm[0])


def test_broadcast_element_keeps_dtype():
    """Test that broadcasting an element keeps the same dtype."""
    element = cheetah.Drift(length=torch.tensor([0.4]), dtype=torch.float64)
    broadcast_element = element.broadcast((3, 10))

    assert broadcast_element.length.dtype == torch.float64


def test_broadcast_beam_keeps_dtype():
    """Test that broadcasting a beam keeps the same dtype."""
    beam = cheetah.ParticleBeam.from_parameters(
        num_particles=100_000, sigma_x=torch.tensor([1e-5]), dtype=torch.float64
    )
    broadcast_beam = beam.broadcast((2,))
    drift = cheetah.Drift(length=torch.tensor([0.4, 0.4]), dtype=torch.float64)

    assert broadcast_beam.particles.dtype == torch.float64

    # This should not raise an error
    _ = drift(broadcast_beam)


def test_broadcast_drift():
    """Test that broadcasting a `Drift` element gives the correct result."""
    element = cheetah.Drift(length=torch.tensor([0.4]))
    broadcast_element = element.broadcast((3, 10))

    assert broadcast_element.length.shape == (3, 10)
    for i in range(3):
        for j in range(10):
            assert broadcast_element.length[i, j] == 0.4


def test_broadcast_quadrupole():
    """Test that broadcasting a `Quadrupole` element gives the correct result."""

    # TODO Add misalignment to the test
    # TODO Add tilt to the test

    element = cheetah.Quadrupole(length=torch.tensor([0.4]), k1=torch.tensor([4.2]))
    broadcast_element = element.broadcast((3, 10))

    assert broadcast_element.length.shape == (3, 10)
    assert broadcast_element.k1.shape == (3, 10)
    for i in range(3):
        for j in range(10):
            assert broadcast_element.length[i, j] == 0.4
            assert broadcast_element.k1[i, j] == 4.2


def test_cavity_with_zero_and_non_zero_voltage():
    """
    Tests that if zero and non-zero voltages are passed to a cavity in a single batch,
    there are no errors. This test does NOT check physical correctness.
    """
    cavity = cheetah.Cavity(
        length=torch.tensor([3.0441, 3.0441, 3.0441]),
        voltage=torch.tensor([0.0, 48198468.0, 0.0]),
        phase=torch.tensor([48198468.0, 48198468.0, 48198468.0]),
        frequency=torch.tensor([2.8560e09, 2.8560e09, 2.8560e09]),
        name="my_test_cavity",
    )
    beam = cheetah.ParticleBeam.from_parameters(
        num_particles=100_000, sigma_x=torch.tensor([1e-5])
    ).broadcast((3,))

    _ = cavity.track(beam)


def test_screen_length_shape():
    """
    Test that the shape of a screen's length matches the shape of its misalignment.
    """
    screen = cheetah.Screen(misalignment=torch.tensor([[0.1, 0.2], [0.3, 0.4]]))
    assert screen.length.shape == screen.misalignment.shape[:-1]


def test_screen_length_broadcast_shape():
    """
    Test that the shape of a screen's length matches the shape of its misalignment
    after broadcasting.
    """
    screen = cheetah.Screen(misalignment=torch.tensor([[0.1, 0.2]]))
    broadcast_screen = screen.broadcast((3, 10))
    assert broadcast_screen.length.shape == broadcast_screen.misalignment.shape[:-1]


def test_vectorized_undulator():
    """Test that a vectorized `Undulator` is able to track a particle beam."""
    element = cheetah.Undulator(length=torch.tensor([0.4, 0.7]))
    beam = cheetah.ParticleBeam.from_parameters(
        num_particles=100_000, sigma_x=torch.tensor([1e-5])
    ).broadcast((2,))

    _ = element.track(beam)


def test_vectorized_solenoid():
    """Test that a vectorized `Solenoid` is able to track a particle beam."""
    element = cheetah.Solenoid(
        length=torch.tensor([0.4, 0.7]), k=torch.tensor([4.2, 3.1])
    )
    beam = cheetah.ParticleBeam.from_parameters(
        num_particles=100_000, sigma_x=torch.tensor([1e-5])
    ).broadcast((2,))

    _ = element.track(beam)
