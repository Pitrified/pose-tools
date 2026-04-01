"""Tests for pose_tools.video.frame."""

import numpy as np
import pytest

from pose_tools.video.frame import Frame


@pytest.fixture
def rgb_array() -> np.ndarray:
    """Small 4x6 RGB image."""
    return np.zeros((4, 6, 3), dtype=np.uint8)


@pytest.fixture
def bgr_array() -> np.ndarray:
    """Small 4x6 BGR image with a known red channel."""
    img = np.zeros((4, 6, 3), dtype=np.uint8)
    img[:, :, 2] = 255  # BGR red channel
    return img


class TestFrameFactories:
    """Factory class-method smoke tests."""

    def test_from_np_array(self, rgb_array: np.ndarray) -> None:
        frame = Frame.from_np_array(rgb_array, msec=100.0, idx=5)
        assert frame.msec == 100.0
        assert frame.idx == 5
        assert frame.to_numpy().shape == (4, 6, 3)

    def test_from_opencv_converts_bgr_to_rgb(self, bgr_array: np.ndarray) -> None:
        frame = Frame.from_opencv(bgr_array, msec=0, idx=0)
        rgb = frame.to_numpy()
        # Original BGR had red in channel 2; RGB should have it in channel 0
        assert rgb[0, 0, 0] == 255
        assert rgb[0, 0, 2] == 0

    def test_from_file(self, tmp_path) -> None:
        import cv2 as cv

        img_path = tmp_path / "test.png"
        img = np.full((10, 10, 3), 128, dtype=np.uint8)
        cv.imwrite(str(img_path), img)

        frame = Frame.from_file(img_path, msec=50.0, idx=1)
        assert frame.idx == 1
        assert frame.to_numpy().shape[:2] == (10, 10)


class TestFrameConversions:
    """to_numpy / to_opencv round-trip."""

    def test_to_opencv_is_bgr(self, rgb_array: np.ndarray) -> None:
        rgb_array[0, 0] = [255, 0, 0]  # red in RGB
        frame = Frame.from_np_array(rgb_array)
        bgr = frame.to_opencv()
        assert bgr[0, 0, 2] == 255  # red now in BGR channel 2
        assert bgr[0, 0, 0] == 0


class TestFrameProperties:
    """Misc properties and repr."""

    def test_usec(self, rgb_array: np.ndarray) -> None:
        frame = Frame.from_np_array(rgb_array, msec=1.5)
        assert frame.usec == 1500

    def test_str(self, rgb_array: np.ndarray) -> None:
        frame = Frame.from_np_array(rgb_array, msec=2.0, idx=3)
        assert "idx=3" in str(frame)
        assert "msec=2.000" in str(frame)
