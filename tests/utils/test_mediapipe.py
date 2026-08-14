"""Tests for pose_tools.utils.mediapipe."""

from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarkerResult
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerResult
import numpy as np
import pytest

from pose_tools.utils.mediapipe import FACE_LANDMARK_COUNT
from pose_tools.utils.mediapipe import FACE_LEFT_IRIS_CENTER
from pose_tools.utils.mediapipe import FACE_LEFT_IRIS_RING
from pose_tools.utils.mediapipe import FACE_MESH_LANDMARK_COUNT
from pose_tools.utils.mediapipe import FACE_RIGHT_IRIS_CENTER
from pose_tools.utils.mediapipe import FACE_RIGHT_IRIS_RING
from pose_tools.utils.mediapipe import HAND_LANDMARK_MAP
from pose_tools.utils.mediapipe import HAND_LANDMARK_NAMES
from pose_tools.utils.mediapipe import POSE_LANDMARK_MAP
from pose_tools.utils.mediapipe import POSE_LANDMARK_NAMES
from pose_tools.utils.mediapipe import UnsupportedLandmarkInfoError
from pose_tools.utils.mediapipe import are_valid_normalized_points
from pose_tools.utils.mediapipe import get_default_face_connections
from pose_tools.utils.mediapipe import get_default_hand_connections
from pose_tools.utils.mediapipe import get_default_pose_connections
from pose_tools.utils.mediapipe import get_face_iris_connections
from pose_tools.utils.mediapipe import get_face_tesselation_connections
from pose_tools.utils.mediapipe import get_facial_transformation_matrix
from pose_tools.utils.mediapipe import get_landmarks_from_result
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

    def test_face_contours_are_lighter_than_the_tesselation(self) -> None:
        contours = len(get_default_face_connections())
        tesselation = len(get_face_tesselation_connections())
        assert contours > 0
        assert contours < tesselation

    def test_face_iris_connections_cover_both_eyes(self) -> None:
        indices = {i for c in get_face_iris_connections() for i in (c.start, c.end)}
        assert indices == set(FACE_LEFT_IRIS_RING) | set(FACE_RIGHT_IRIS_RING)


class TestFaceConstants:
    """The iris indices, checked against MediaPipe's own tables."""

    def test_counts(self) -> None:
        assert FACE_LANDMARK_COUNT == FACE_MESH_LANDMARK_COUNT + 10

    def test_iris_centres_sit_outside_the_mesh(self) -> None:
        # The centres are the two indices no connection table mentions.
        assert FACE_RIGHT_IRIS_CENTER == FACE_MESH_LANDMARK_COUNT
        assert FACE_RIGHT_IRIS_RING[-1] + 1 == FACE_LEFT_IRIS_CENTER

    def test_rings_follow_their_centres(self) -> None:
        assert FACE_RIGHT_IRIS_RING == (469, 470, 471, 472)
        assert FACE_LEFT_IRIS_RING == (474, 475, 476, 477)

    def test_tesselation_stops_before_the_irises(self) -> None:
        indices = {
            i for c in get_face_tesselation_connections() for i in (c.start, c.end)
        }
        assert max(indices) == FACE_MESH_LANDMARK_COUNT - 1


class TestGetLandmarksFromResult:
    """Pulling landmark lists out of the three result types."""

    def test_face_normalized(self) -> None:
        result = FaceLandmarkerResult(
            face_landmarks=[["a", "b"]],  # type: ignore[list-item]
            face_blendshapes=[],
            facial_transformation_matrixes=[],
        )
        assert get_landmarks_from_result(result, "normalized") == ["a", "b"]

    def test_face_index_out_of_range(self) -> None:
        result = FaceLandmarkerResult(
            face_landmarks=[["a"]],  # type: ignore[list-item]
            face_blendshapes=[],
            facial_transformation_matrixes=[],
        )
        assert get_landmarks_from_result(result, "normalized", idx=3) is None

    def test_face_world_is_unsupported(self) -> None:
        result = FaceLandmarkerResult(
            face_landmarks=[["a"]],  # type: ignore[list-item]
            face_blendshapes=[],
            facial_transformation_matrixes=[],
        )
        with pytest.raises(UnsupportedLandmarkInfoError, match="world"):
            get_landmarks_from_result(result, "world")  # type: ignore[call-overload]

    def test_pose_handedness_is_unsupported(self) -> None:
        result = PoseLandmarkerResult(
            pose_landmarks=[["a"]],  # type: ignore[list-item]
            pose_world_landmarks=[],
            segmentation_masks=None,
        )
        with pytest.raises(UnsupportedLandmarkInfoError, match="handedness"):
            get_landmarks_from_result(result, "handedness")  # type: ignore[call-overload]


class TestFacialTransformationMatrix:
    """The head pose matrix, which is absent unless asked for."""

    def test_returns_the_matrix(self) -> None:
        matrix = np.eye(4)
        result = FaceLandmarkerResult(
            face_landmarks=[["a"]],  # type: ignore[list-item]
            face_blendshapes=[],
            facial_transformation_matrixes=[matrix],
        )
        got = get_facial_transformation_matrix(result)
        assert got is not None
        assert np.array_equal(got, matrix)

    def test_none_when_the_option_was_off(self) -> None:
        result = FaceLandmarkerResult(
            face_landmarks=[["a"]],  # type: ignore[list-item]
            face_blendshapes=[],
            facial_transformation_matrixes=[],
        )
        assert get_facial_transformation_matrix(result) is None

    def test_none_when_the_face_index_is_out_of_range(self) -> None:
        result = FaceLandmarkerResult(
            face_landmarks=[["a"]],  # type: ignore[list-item]
            face_blendshapes=[],
            facial_transformation_matrixes=[np.eye(4)],
        )
        assert get_facial_transformation_matrix(result, idx=2) is None


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
