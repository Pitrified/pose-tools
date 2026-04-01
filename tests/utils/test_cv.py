"""Tests for pose_tools.utils.cv."""

import numpy as np

from pose_tools.utils.cv import resize


class TestResize:
    """Aspect-ratio-preserving resize."""

    def test_wider_than_tall(self) -> None:
        img = np.zeros((100, 200, 3), dtype=np.uint8)
        out = resize(img, desired_width=400, desired_height=300)
        assert out.shape[1] == 400
        assert out.shape[0] == 200  # scaled proportionally

    def test_taller_than_wide(self) -> None:
        img = np.zeros((200, 100, 3), dtype=np.uint8)
        out = resize(img, desired_width=400, desired_height=300)
        assert out.shape[0] == 300
        assert out.shape[1] == 150  # scaled proportionally

    def test_square_image(self) -> None:
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        out = resize(img, desired_width=640, desired_height=480)
        # square -> h >= w, so takes the taller-than-wide branch
        assert out.shape[0] == 480
