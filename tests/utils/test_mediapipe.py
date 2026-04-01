"""Tests for pose_tools.utils.mediapipe."""

import numpy as np

from pose_tools.utils.mediapipe import HAND_LANDMARK_MAP
from pose_tools.utils.mediapipe import HAND_LANDMARK_NAMES
from pose_tools.utils.mediapipe import POSE_LANDMARK_MAP
from pose_tools.utils.mediapipe import POSE_LANDMARK_NAMES
from pose_tools.utils.mediapipe import are_valid_normalized_points
from pose_tools.utils.mediapipe import get_default_hand_connections
from pose_tools.utils.mediapipe import get_default_pose_connections
from pose_tools.utils.mediapipe import normalized_to_pixel_coordinates


class TestLandmarkConstants:
    """Landmark name/map sanity checks."""

    def test_pose_landmark_names_nonempty(self) -> None:
        assert len(POSE_LANDMARK_NAMES) > 0
        assert "NOSE" in POSE_LANDMARK_NAMES

    def test_hand_landmark_names_nonempty(self) -> None:
        assert len(HAND_LANDMARK_NAMES) > 0
        assert "WRIST" in HAND_LANDMARK_NAMES

    def test_pose_map_matches_names(self) -> None:
        for name in POSE_LANDMARK_NAMES:
            assert name in POSE_LANDMARK_MAP

    def test_hand_map_matches_names(self) -> None:
        for name in HAND_LANDMARK_NAMES:
            assert name in HAND_LANDMARK_MAP


class TestConnections:
    """Default connection lists."""

    def test_pose_connections_nonempty(self) -> None:
        conns = get_default_pose_connections()
        assert len(conns) > 0
        # Connection objects have .start and .end attributes
        assert hasattr(conns[0], "start")
        assert hasattr(conns[0], "end")

    def test_hand_connections_nonempty(self) -> None:
        conns = get_default_hand_connections()
        assert len(conns) > 0


class TestNormalizedToPixelCoordinates:
    """Batch coordinate conversion."""

    def test_basic_conversion(self) -> None:
        pts = np.array([[0.5, 0.5], [0.0, 1.0]])
        result = normalized_to_pixel_coordinates(pts, image_size=(100, 200))
        # (0.5 * 200, 0.5 * 100) = (100, 50)
        assert result[0, 0] == 100
        assert result[0, 1] == 50

    def test_clipping(self) -> None:
        pts = np.array([[1.5, -0.1]])
        result = normalized_to_pixel_coordinates(
            pts, image_size=(100, 200), clip_to_image=True
        )
        assert result[0, 0] == 199  # clipped to width-1
        assert result[0, 1] == 0  # clipped to 0

    def test_no_clipping(self) -> None:
        pts = np.array([[1.5, -0.1]])
        result = normalized_to_pixel_coordinates(
            pts, image_size=(100, 200), clip_to_image=False
        )
        assert result[0, 0] > 199


class TestAreValidNormalizedPoints:
    """Point validation."""

    def test_valid_points(self) -> None:
        pts = np.array([[0.0, 0.0], [0.5, 0.5], [1.0, 1.0]])
        result = are_valid_normalized_points(pts)
        assert result.all()

    def test_out_of_range(self) -> None:
        pts = np.array([[0.5, 0.5], [-0.1, 0.5], [0.5, 1.1]])
        result = are_valid_normalized_points(pts)
        assert result[0]
        assert not result[1]
        assert not result[2]
