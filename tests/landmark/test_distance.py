"""Tests for pose_tools.landmark.distance."""

from enum import IntEnum

import numpy as np

from pose_tools.landmark.distance import compute_landmark_dist
from pose_tools.landmark.distance import compute_pinch_level


class FakeLandmark:
    """Minimal landmark stub."""

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


class FakeMap(IntEnum):
    """Two-landmark map for testing."""

    A = 0
    B = 1


class TestComputeLandmarkDist:
    """Euclidean distance between named landmarks."""

    def test_known_distance(self) -> None:
        landmarks = [FakeLandmark(0, 0, 0), FakeLandmark(3, 4, 0)]
        landmark_map: dict[str, IntEnum] = {"A": FakeMap.A, "B": FakeMap.B}
        dist = compute_landmark_dist(landmarks, landmark_map, "A", "B")  # type: ignore[arg-type]
        assert np.isclose(dist, 5.0)

    def test_zero_distance(self) -> None:
        landmarks = [FakeLandmark(1, 2, 3), FakeLandmark(1, 2, 3)]
        landmark_map: dict[str, IntEnum] = {"A": FakeMap.A, "B": FakeMap.B}
        dist = compute_landmark_dist(landmarks, landmark_map, "A", "B")  # type: ignore[arg-type]
        assert np.isclose(dist, 0.0)


class TestComputePinchLevel:
    """Pinch metric is ratio of two distances."""

    def test_pinch_ratio(self) -> None:
        # Create a minimal hand-like landmark list with enough entries
        # HandLandmark: WRIST=0, THUMB_TIP=4, INDEX_FINGER_TIP=8, INDEX_FINGER_MCP=5
        landmarks = [FakeLandmark(0, 0, 0)] * 21
        landmarks[0] = FakeLandmark(0, 0, 0)  # WRIST
        landmarks[4] = FakeLandmark(1, 0, 0)  # THUMB_TIP
        landmarks[5] = FakeLandmark(0, 2, 0)  # INDEX_FINGER_MCP
        landmarks[8] = FakeLandmark(1, 0, 0)  # INDEX_FINGER_TIP

        from pose_tools.utils.mediapipe import HAND_LANDMARK_MAP

        pinch = compute_pinch_level(landmarks, HAND_LANDMARK_MAP)  # type: ignore[arg-type]
        # dist(thumb_tip, index_tip) = 0 (same position)
        # dist(wrist, index_mcp) = 2
        assert np.isclose(pinch, 0.0)
