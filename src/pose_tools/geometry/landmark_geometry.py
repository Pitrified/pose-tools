"""Geometric coordinate transforms for landmarks.

Provides batch conversion between normalized [0,1] and pixel coordinates,
and validation of normalized points.

Note:
    The core functions ``normalized_to_pixel_coordinates`` and
    ``are_valid_normalized_points`` are canonical in
    ``pose_tools.utils.mediapipe``. This module re-exports them and
    adds higher-level geometric helpers as needed.
"""

from pose_tools.utils.mediapipe import are_valid_normalized_points
from pose_tools.utils.mediapipe import normalized_to_pixel_coordinates

__all__ = [
    "are_valid_normalized_points",
    "normalized_to_pixel_coordinates",
]
