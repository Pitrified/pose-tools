"""Landmark distance computation utilities."""

from collections.abc import Sequence
from enum import IntEnum

from mediapipe.tasks.python.components.containers.landmark import Landmark
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark
import numpy as np


def compute_landmark_dist(
    landmarks: Sequence[Landmark] | Sequence[NormalizedLandmark],
    landmark_map: dict[str, IntEnum],
    name1: str,
    name2: str,
) -> float:
    """Compute the Euclidean distance between two named landmarks.

    Works with both world (``Landmark``) and normalized
    (``NormalizedLandmark``) landmarks.

    Args:
        landmarks: List of landmark objects.
        landmark_map: Name-to-index mapping (e.g. ``HAND_LANDMARK_MAP``).
        name1: First landmark name.
        name2: Second landmark name.
    """
    lm1 = landmarks[landmark_map[name1]]
    lm2 = landmarks[landmark_map[name2]]
    dist: float = np.linalg.norm(
        np.array([lm1.x, lm1.y, lm1.z]) - np.array([lm2.x, lm2.y, lm2.z])
    ).item()
    return dist


def compute_pinch_level(
    hand_world_landmarks: Sequence[Landmark],
    landmark_map: dict[str, IntEnum],
) -> float:
    """Compute a normalized pinch metric.

    The pinch level is the ratio of the thumb-tip to index-finger-tip
    distance over the wrist to index-finger-MCP distance. Lower values
    indicate a tighter pinch.

    Args:
        hand_world_landmarks: World landmarks for one hand.
        landmark_map: Hand landmark name-to-index mapping.
    """
    dist_thumb_index = compute_landmark_dist(
        hand_world_landmarks, landmark_map, "THUMB_TIP", "INDEX_FINGER_TIP"
    )
    dist_wrist_index = compute_landmark_dist(
        hand_world_landmarks, landmark_map, "WRIST", "INDEX_FINGER_MCP"
    )
    return dist_thumb_index / dist_wrist_index
