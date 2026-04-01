"""Tests for pose_tools.geometry.signal_tracker."""

from pose_tools.geometry.signal_tracker import SignalTracker


class TestSignalTracker:
    """Stateful signal tracking with derivative classification."""

    def test_initial_state(self) -> None:
        tracker = SignalTracker(sd_max=1.0, sd_min=0.01, sdsd_max=0.5)
        assert not tracker.is_active
        assert len(tracker.all_values) == 0

    def test_update_appends_history(self) -> None:
        tracker = SignalTracker(sd_max=1.0, sd_min=0.01, sdsd_max=0.5)
        for v in [0.1, 0.2, 0.3, 0.4, 0.5]:
            tracker.update(v)
        assert len(tracker.all_values) == 5
        assert len(tracker.all_values_s) == 5
        assert len(tracker.all_is_active) == 5

    def test_constant_signal_inactive(self) -> None:
        """A constant signal has zero derivative - below sd_min threshold."""
        tracker = SignalTracker(sd_max=1.0, sd_min=0.01, sdsd_max=0.5)
        for _ in range(20):
            tracker.update(1.0)
        assert not tracker.is_active

    def test_linear_ramp_activation(self) -> None:
        """A steady linear ramp should eventually activate."""
        tracker = SignalTracker(sd_max=10.0, sd_min=0.001, sdsd_max=10.0, filter_size=3)
        for i in range(30):
            tracker.update(float(i) * 0.1)
        # With these generous thresholds the ramp should be active
        assert tracker.is_active

    def test_returns_float(self) -> None:
        tracker = SignalTracker(sd_max=1.0, sd_min=0.01, sdsd_max=0.5)
        result = tracker.update(0.5)
        assert isinstance(result, float)
