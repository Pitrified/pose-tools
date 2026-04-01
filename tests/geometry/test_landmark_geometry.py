"""Tests for pose_tools.geometry.landmark_geometry (re-export module)."""

from pose_tools.geometry.landmark_geometry import are_valid_normalized_points
from pose_tools.geometry.landmark_geometry import normalized_to_pixel_coordinates


def test_reexports_are_callable() -> None:
    """Verify that re-exports are the same functions from utils.mediapipe."""
    from pose_tools.utils.mediapipe import are_valid_normalized_points as orig_valid
    from pose_tools.utils.mediapipe import normalized_to_pixel_coordinates as orig_n2p

    assert normalized_to_pixel_coordinates is orig_n2p
    assert are_valid_normalized_points is orig_valid
