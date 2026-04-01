"""Tests for pose_tools.utils.np_signal."""

import numpy as np

from pose_tools.utils.np_signal import create_left_triangle_filter
from pose_tools.utils.np_signal import diff_pad
from pose_tools.utils.np_signal import roll_append
from pose_tools.utils.np_signal import roll_append_smooth


class TestDiffPad:
    """diff_pad preserves length and prepads."""

    def test_basic(self) -> None:
        x = np.array([1.0, 3.0, 6.0, 10.0])
        result = diff_pad(x)
        assert len(result) == len(x)
        np.testing.assert_allclose(result, [0.0, 2.0, 3.0, 4.0])

    def test_single_element(self) -> None:
        x = np.array([5.0])
        result = diff_pad(x)
        np.testing.assert_allclose(result, [0.0])


class TestCreateLeftTriangleFilter:
    """Triangle filter properties."""

    def test_sums_to_one(self) -> None:
        filt = create_left_triangle_filter(10)
        assert np.isclose(filt.sum(), 1.0)

    def test_monotonically_increasing(self) -> None:
        filt = create_left_triangle_filter(5)
        assert all(filt[i] < filt[i + 1] for i in range(len(filt) - 1))

    def test_length(self) -> None:
        filt = create_left_triangle_filter(7)
        assert len(filt) == 7


class TestRollAppend:
    """roll_append shifts left and appends."""

    def test_basic(self) -> None:
        x = np.array([1.0, 2.0, 3.0])
        result = roll_append(x, 99.0)
        np.testing.assert_allclose(result, [2.0, 3.0, 99.0])


class TestRollAppendSmooth:
    """roll_append_smooth returns updated histories."""

    def test_basic_smoothing(self) -> None:
        filt = create_left_triangle_filter(3)
        hist = np.array([0.0, 0.0, 0.0])
        hist_s = np.array([0.0, 0.0, 0.0])

        hist, hist_s = roll_append_smooth(hist, hist_s, 6.0, filt)
        # After one update: hist = [0, 0, 6], smoothed = dot([0,0,6], filt)
        assert hist[-1] == 6.0
        # The smoothed value should be the weighted sum
        expected_smooth = np.dot(np.array([0.0, 0.0, 6.0]), filt)
        assert np.isclose(hist_s[-1], expected_smooth)
