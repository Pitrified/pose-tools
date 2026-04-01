"""Tests for pose_tools.geometry.homography."""

import cv2 as cv
import numpy as np
import pytest

from pose_tools.geometry.homography import InsufficientMatchesError
from pose_tools.geometry.homography import compute_homography
from pose_tools.geometry.homography import perspective_transform


class TestPerspectiveTransform:
    """Apply a known transformation to points."""

    def test_identity(self) -> None:
        pts = np.array([[10.0, 20.0], [30.0, 40.0]])
        identity = np.eye(3)
        result = perspective_transform(pts, identity)
        np.testing.assert_allclose(result, pts, atol=1e-6)

    def test_translation(self) -> None:
        pts = np.array([[0.0, 0.0]])
        # Translation by (5, 10) via homography
        mat = np.array([[1, 0, 5], [0, 1, 10], [0, 0, 1]], dtype=float)
        result = perspective_transform(pts, mat)
        np.testing.assert_allclose(result[0], [5.0, 10.0], atol=1e-6)

    def test_empty_points(self) -> None:
        pts = np.empty((0, 2))
        result = perspective_transform(pts, np.eye(3))
        assert len(result) == 0


class TestComputeHomography:
    """SIFT-based homography (requires feature-rich images)."""

    def test_identical_images(self) -> None:
        """Same image should produce an identity-like homography."""
        rng = np.random.default_rng(42)
        img = rng.integers(0, 255, size=(200, 300, 3), dtype=np.uint8)
        # Add some texture
        for _ in range(50):
            x, y = rng.integers(0, 290), rng.integers(0, 190)
            cv.circle(img, (int(x), int(y)), 5, (255, 255, 255), -1)

        h = compute_homography(img, img, min_match_count=4)
        np.testing.assert_allclose(h, np.eye(3), atol=0.1)

    def test_insufficient_matches_raises(self) -> None:
        """Two blank images have no features."""
        img1 = np.zeros((50, 50, 3), dtype=np.uint8)
        img2 = np.full((50, 50, 3), 128, dtype=np.uint8)
        with pytest.raises((InsufficientMatchesError, cv.error)):
            compute_homography(img1, img2, min_match_count=10)
