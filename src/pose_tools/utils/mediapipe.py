"""Shared MediaPipe utilities for landmark detection.

Provides landmark name/map constants, connection lists, and drawing spec
helpers used by the pose, hand and face detection pipelines.

All imports target the Tasks API (``mediapipe.tasks.python.vision.*``)
which is the API surface available in mediapipe >= 0.10.
"""

from collections.abc import Mapping
from enum import IntEnum
from typing import Literal
from typing import cast
from typing import overload

from mediapipe.tasks.python.components.containers.category import Category
from mediapipe.tasks.python.components.containers.landmark import Landmark
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark
from mediapipe.tasks.python.vision import HandLandmarksConnections
from mediapipe.tasks.python.vision import PoseLandmark
from mediapipe.tasks.python.vision import PoseLandmarksConnections
from mediapipe.tasks.python.vision.drawing_utils import DrawingSpec
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarkerResult
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarksConnections
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerResult
import numpy as np

# --- Pose landmark constants ---
POSE_LANDMARK_NAMES: list[str] = PoseLandmark._member_names_
POSE_LANDMARK_MAP: dict[str, IntEnum] = cast(
    "dict[str, IntEnum]", PoseLandmark._member_map_
)

# --- Hand landmark constants ---
HAND_LANDMARK_NAMES: list[str] = HandLandmark._member_names_
HAND_LANDMARK_MAP: dict[str, IntEnum] = cast(
    "dict[str, IntEnum]", HandLandmark._member_map_
)


# --- Face landmark constants ---
# The face mesh is 468 points, indices 0-467, plus ten iris points. Each iris is
# a centre followed by a four-point ring; only the rings appear in the
# connection tables, so the centres are named here or they are unreachable.
FACE_LANDMARK_COUNT = 478
FACE_MESH_LANDMARK_COUNT = 468

FACE_RIGHT_IRIS_CENTER = 468
FACE_RIGHT_IRIS_RING: tuple[int, ...] = (469, 470, 471, 472)
FACE_LEFT_IRIS_CENTER = 473
FACE_LEFT_IRIS_RING: tuple[int, ...] = (474, 475, 476, 477)


class UnsupportedLandmarkInfoError(ValueError):
    """Raised when a result type does not carry the requested landmark info."""

    def __init__(self, result_type: str, which_info: str) -> None:
        """Initialise with the result type and the info it cannot provide.

        Args:
            result_type: Name of the landmarker result class.
            which_info: The landmark info that was asked for.
        """
        super().__init__(f"{result_type} does not have {which_info} info.")


def get_default_pose_connections() -> list:
    """Return the default pose skeleton connections."""
    return PoseLandmarksConnections.POSE_LANDMARKS


def get_default_hand_connections() -> list:
    """Return the default hand skeleton connections."""
    return HandLandmarksConnections.HAND_CONNECTIONS


def get_default_face_connections() -> list:
    """Return the face contour connections, the readable default."""
    return FaceLandmarksConnections.FACE_LANDMARKS_CONTOURS


def get_face_tesselation_connections() -> list:
    """Return the full face mesh connections."""
    return FaceLandmarksConnections.FACE_LANDMARKS_TESSELATION


def get_face_iris_connections() -> list:
    """Return both iris rings as one connection list."""
    return [
        *FaceLandmarksConnections.FACE_LANDMARKS_LEFT_IRIS,
        *FaceLandmarksConnections.FACE_LANDMARKS_RIGHT_IRIS,
    ]


def get_spec_from_map(
    drawing_spec: DrawingSpec | Mapping[object, DrawingSpec],
    key: object,
) -> DrawingSpec:
    """Extract a ``DrawingSpec`` from a mapping, or return it unchanged."""
    if isinstance(drawing_spec, Mapping):
        return drawing_spec[key]
    return drawing_spec


# --- get_landmarks_from_result: pose overloads ---


@overload
def get_landmarks_from_result(
    result: PoseLandmarkerResult,
    which_info: Literal["world"],
    idx: int = 0,
) -> list[Landmark] | None: ...


@overload
def get_landmarks_from_result(
    result: PoseLandmarkerResult,
    which_info: Literal["normalized"],
    idx: int = 0,
) -> list[NormalizedLandmark] | None: ...


# --- get_landmarks_from_result: hand overloads ---


@overload
def get_landmarks_from_result(
    result: HandLandmarkerResult,
    which_info: Literal["world"],
    idx: int = 0,
) -> list[Landmark] | None: ...


@overload
def get_landmarks_from_result(
    result: HandLandmarkerResult,
    which_info: Literal["normalized"],
    idx: int = 0,
) -> list[NormalizedLandmark] | None: ...


@overload
def get_landmarks_from_result(
    result: HandLandmarkerResult,
    which_info: Literal["handedness"],
    idx: int = 0,
) -> list[Category] | None: ...


# --- get_landmarks_from_result: face overloads ---
# Face results carry normalized landmarks only: there is no face equivalent of
# pose_world_landmarks, so "world" has no overload and raises at runtime.


@overload
def get_landmarks_from_result(
    result: FaceLandmarkerResult,
    which_info: Literal["normalized"],
    idx: int = 0,
) -> list[NormalizedLandmark] | None: ...


def get_landmarks_from_result(
    result: PoseLandmarkerResult | HandLandmarkerResult | FaceLandmarkerResult,
    which_info: Literal["world", "normalized", "handedness"] = "normalized",
    idx: int = 0,
) -> list[Landmark] | list[NormalizedLandmark] | list[Category] | None:
    """Extract landmark data from a pose, hand or face landmarker result.

    Args:
        result: A ``PoseLandmarkerResult``, ``HandLandmarkerResult`` or
            ``FaceLandmarkerResult``.
        which_info: Which landmark list to retrieve.
        idx: Index of the detected person/hand/face (default 0).

    Returns:
        The requested landmark list, or ``None`` if *idx* is out of range.

    Raises:
        UnsupportedLandmarkInfoError: If the result type does not carry
            *which_info*, e.g. handedness on a pose result or world landmarks
            on a face result.
    """
    if isinstance(result, HandLandmarkerResult):
        if which_info == "world":
            ll = result.hand_world_landmarks
        elif which_info == "normalized":
            ll = result.hand_landmarks
        else:
            ll = result.handedness
    elif isinstance(result, FaceLandmarkerResult):
        if which_info != "normalized":
            raise UnsupportedLandmarkInfoError(type(result).__name__, which_info)
        ll = result.face_landmarks
    else:
        if which_info == "handedness":
            raise UnsupportedLandmarkInfoError(type(result).__name__, which_info)
        if which_info == "world":
            ll = result.pose_world_landmarks
        else:
            ll = result.pose_landmarks

    if idx >= len(ll):
        return None
    return ll[idx]


def get_facial_transformation_matrix(
    result: FaceLandmarkerResult,
    idx: int = 0,
) -> np.ndarray | None:
    """Extract a face's 4x4 head pose matrix, relative to the camera.

    The field is an empty list unless the landmarker was built with
    ``output_facial_transformation_matrixes=True``, so a missing matrix and a
    missing face are the same answer here: ``None``.

    Args:
        result: A face landmarker result.
        idx: Index of the detected face (default 0).

    Returns:
        A ``(4, 4)`` array, or ``None`` if the option was off or *idx* is out
        of range.
    """
    matrixes = result.facial_transformation_matrixes
    if matrixes is None or idx >= len(matrixes):
        return None
    return np.asarray(matrixes[idx])


def normalized_to_pixel_coordinates(
    normalized_points: np.ndarray,
    image_size: tuple[int, int],
    *,
    clip_to_image: bool = True,
) -> np.ndarray:
    """Convert normalized [0,1] coordinates to pixel coordinates.

    Args:
        normalized_points: Array of shape ``(N, 2)`` with values in [0, 1].
        image_size: ``(height, width)`` of the target image.
        clip_to_image: Clamp results to image bounds.

    Returns:
        Integer pixel coordinates of shape ``(N, 2)``.
    """
    image_height, image_width = image_size
    x_px = np.floor(normalized_points[:, 0] * image_width).astype(int)
    y_px = np.floor(normalized_points[:, 1] * image_height).astype(int)
    if clip_to_image:
        x_px = np.clip(x_px, 0, image_width - 1)
        y_px = np.clip(y_px, 0, image_height - 1)
    return np.column_stack((x_px, y_px))


def are_valid_normalized_points(points: np.ndarray) -> np.ndarray:
    """Check whether points lie within the [0, 1] range.

    Args:
        points: Array of shape ``(N, 2)``.

    Returns:
        Boolean array of shape ``(N,)``.
    """
    zeros = (points > 0) | np.isclose(points, 0)
    ones = (points < 1) | np.isclose(points, 1)
    valid = zeros & ones
    return np.asarray(valid.all(axis=1))
