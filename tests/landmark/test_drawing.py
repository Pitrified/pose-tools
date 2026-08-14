"""Tests for pose_tools.landmark.drawing.

MediaPipe's ``draw_landmarks`` is patched out: what these tests pin is the
wrapper logic around it - which connections and style each call selects, that
the source image is never mutated, and that an empty result is a warning rather
than an exception.
"""

from typing import Any

from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarkerResult
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerResult
import numpy as np
import pytest

from pose_tools.landmark import drawing
from pose_tools.landmark.drawing import draw_face_landmarks
from pose_tools.landmark.drawing import draw_pose_landmarks
from pose_tools.utils.mediapipe import get_default_face_connections
from pose_tools.utils.mediapipe import get_face_iris_connections
from pose_tools.utils.mediapipe import get_face_tesselation_connections
from pose_tools.video.frame import Frame


class FakeImage:
    """Stand-in for a MediaPipe Image, which only needs to yield an array."""

    def __init__(self, array: np.ndarray) -> None:
        self._array = array

    def numpy_view(self) -> np.ndarray:
        return self._array


@pytest.fixture
def frame() -> Frame:
    """Build a small RGB frame."""
    image = np.zeros((4, 4, 3), dtype=np.uint8)
    return Frame(image=FakeImage(image), msec=0.0, idx=0)  # type: ignore[arg-type]


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Record every ``draw_landmarks`` call instead of drawing."""
    recorded: list[dict[str, Any]] = []

    def fake_draw(
        image: np.ndarray,
        landmark_list: object,
        connections: object = None,
        landmark_drawing_spec: object = None,
        connection_drawing_spec: object = None,
    ) -> None:
        recorded.append(
            {
                "image": image,
                "landmarks": landmark_list,
                "connections": connections,
                "landmark_spec": landmark_drawing_spec,
            }
        )

    monkeypatch.setattr(drawing.mp_drawing_utils, "draw_landmarks", fake_draw)
    return recorded


def face_result(landmarks: list | None = None) -> FaceLandmarkerResult:
    """Build a face result carrying *landmarks* for one face."""
    faces = [] if landmarks is None else [landmarks]
    return FaceLandmarkerResult(
        face_landmarks=faces,  # type: ignore[arg-type]
        face_blendshapes=[],
        facial_transformation_matrixes=[],
    )


class TestDrawFaceLandmarks:
    """The face drawing wrapper."""

    def test_draws_contours_and_irises_by_default(
        self, frame: Frame, calls: list[dict[str, Any]]
    ) -> None:
        draw_face_landmarks(frame, face_result(["lm"]))

        assert len(calls) == 2
        assert calls[0]["connections"] == get_default_face_connections()
        assert calls[1]["connections"] == get_face_iris_connections()

    def test_tesselation_on_request(
        self, frame: Frame, calls: list[dict[str, Any]]
    ) -> None:
        draw_face_landmarks(frame, face_result(["lm"]), mesh="tesselation")

        assert calls[0]["connections"] == get_face_tesselation_connections()

    def test_irises_can_be_skipped(
        self, frame: Frame, calls: list[dict[str, Any]]
    ) -> None:
        draw_face_landmarks(frame, face_result(["lm"]), draw_irises=False)

        assert len(calls) == 1

    def test_no_landmark_dots(
        self, frame: Frame, calls: list[dict[str, Any]]
    ) -> None:
        # 478 dots would be the whole picture; connections only.
        draw_face_landmarks(frame, face_result(["lm"]))

        assert all(call["landmark_spec"] is None for call in calls)

    def test_missing_face_warns_and_returns_a_copy(
        self, frame: Frame, calls: list[dict[str, Any]]
    ) -> None:
        out = draw_face_landmarks(frame, face_result(None))

        assert calls == []
        assert np.array_equal(out, frame.image.numpy_view())

    @pytest.mark.usefixtures("calls")
    def test_source_image_is_not_mutated(self, frame: Frame) -> None:
        out = draw_face_landmarks(frame, face_result(["lm"]))
        out[0, 0, 0] = 255

        assert frame.image.numpy_view()[0, 0, 0] == 0
        assert out.shape == frame.image.numpy_view().shape
        assert out.dtype == frame.image.numpy_view().dtype


class TestDrawPoseLandmarks:
    """The pose wrapper, previously untested."""

    def test_draws_the_requested_pose(
        self, frame: Frame, calls: list[dict[str, Any]]
    ) -> None:
        result = PoseLandmarkerResult(
            pose_landmarks=[["first"], ["second"]],  # type: ignore[list-item]
            pose_world_landmarks=[],
            segmentation_masks=None,
        )
        draw_pose_landmarks(frame, result, pose_idx=1)

        assert calls[0]["landmarks"] == ["second"]

    def test_missing_pose_warns_and_returns_a_copy(
        self, frame: Frame, calls: list[dict[str, Any]]
    ) -> None:
        result = PoseLandmarkerResult(
            pose_landmarks=[],
            pose_world_landmarks=[],
            segmentation_masks=None,
        )
        out = draw_pose_landmarks(frame, result)

        assert calls == []
        assert np.array_equal(out, frame.image.numpy_view())
