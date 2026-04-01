"""Tests for pose_tools.landmark.landmark_array."""

from pose_tools.landmark.landmark_array import LandmarkArray
from pose_tools.landmark.landmark_array import LandmarkArrayImg


def _make_fake_landmarks(n: int = 5) -> list:
    """Create fake landmark-like objects with .x, .y, .visibility."""

    class FakeLM:
        def __init__(self, x: float, y: float, vis: float) -> None:
            self.x = x
            self.y = y
            self.visibility = vis

    return [FakeLM(i / n, i / n, 0.9 if i % 2 == 0 else 0.3) for i in range(n)]


class TestLandmarkArray:
    """LandmarkArray base class."""

    def test_from_normalized_landmarks(self) -> None:
        lms = _make_fake_landmarks(5)
        arr = LandmarkArray.from_normalized_landmarks(lms)
        assert len(arr) == 5
        assert arr.landmarks_norm.shape == (5, 2)
        assert arr.visibility.shape == (5,)

    def test_repr(self) -> None:
        lms = _make_fake_landmarks(3)
        arr = LandmarkArray.from_normalized_landmarks(lms)
        text = repr(arr)
        assert "v=" in text


class TestLandmarkArrayImg:
    """LandmarkArrayImg - pixel coordinates and drawable."""

    def test_pixel_coordinates(self) -> None:
        lms = _make_fake_landmarks(5)
        arr = LandmarkArrayImg.from_normalized_landmarks(
            lms, image_size=(100, 200), visibility_threshold=0.5
        )
        assert arr.landmarks_img.shape == (5, 2)

    def test_drawable_mask(self) -> None:
        lms = _make_fake_landmarks(5)
        arr = LandmarkArrayImg.from_normalized_landmarks(
            lms, image_size=(100, 200), visibility_threshold=0.5
        )
        # Landmarks with vis=0.9 (even indices) should be drawable if in range
        # Landmarks with vis=0.3 (odd indices) should NOT be drawable
        for i in range(5):
            if lms[i].visibility <= 0.5:
                assert not arr.drawable[i]

    def test_copy(self) -> None:
        lms = _make_fake_landmarks(5)
        arr = LandmarkArrayImg.from_normalized_landmarks(lms, image_size=(100, 200))
        arr2 = arr.copy()
        arr2.landmarks_norm[0, 0] = 999.0
        assert arr.landmarks_norm[0, 0] != 999.0

    def test_str(self) -> None:
        lms = _make_fake_landmarks(5)
        arr = LandmarkArrayImg.from_normalized_landmarks(lms, image_size=(100, 200))
        assert "drawable" in str(arr)
