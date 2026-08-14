"""Drawing utilities for pose, hand and face landmarks."""

from typing import Literal

from loguru import logger as lg
from mediapipe.tasks.python.vision import drawing_styles as mp_drawing_styles
from mediapipe.tasks.python.vision import drawing_utils as mp_drawing_utils
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarkerResult
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerResult
import numpy as np

from pose_tools.utils.mediapipe import get_default_face_connections
from pose_tools.utils.mediapipe import get_default_hand_connections
from pose_tools.utils.mediapipe import get_default_pose_connections
from pose_tools.utils.mediapipe import get_face_iris_connections
from pose_tools.utils.mediapipe import get_face_tesselation_connections
from pose_tools.utils.mediapipe import get_landmarks_from_result
from pose_tools.video.frame import Frame

FaceMeshStyle = Literal["contours", "tesselation"]


def draw_pose_landmarks(
    frame: Frame,
    detection_result: PoseLandmarkerResult,
    pose_idx: int = 0,
) -> np.ndarray:
    """Draw pose landmarks on a copy of the frame's image.

    Args:
        frame: Source frame.
        detection_result: Pose detection result.
        pose_idx: Which detected pose to draw (default first).

    Returns:
        Annotated RGB numpy array.
    """
    rgb_image = np.copy(frame.image.numpy_view())

    pose_landmarks = get_landmarks_from_result(
        detection_result, "normalized", idx=pose_idx
    )
    if pose_landmarks is None:
        lg.warning("No pose landmarks detected.")
        return rgb_image

    mp_drawing_utils.draw_landmarks(
        rgb_image,
        pose_landmarks,
        get_default_pose_connections(),
        mp_drawing_styles.get_default_pose_landmarks_style(),
    )

    return rgb_image


def draw_hand_landmarks(
    frame: Frame,
    detection_result: HandLandmarkerResult,
) -> np.ndarray:
    """Draw hand landmarks on a copy of the frame's image.

    Draws all detected hands.

    Args:
        frame: Source frame.
        detection_result: Hand detection result.

    Returns:
        Annotated RGB numpy array.
    """
    rgb_image = np.copy(frame.image.numpy_view())

    for hand_landmarks in detection_result.hand_landmarks:
        mp_drawing_utils.draw_landmarks(
            rgb_image,
            hand_landmarks,
            get_default_hand_connections(),
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style(),
        )

    return rgb_image


def draw_face_landmarks(
    frame: Frame,
    detection_result: FaceLandmarkerResult,
    face_idx: int = 0,
    mesh: FaceMeshStyle = "contours",
    *,
    draw_irises: bool = True,
) -> np.ndarray:
    """Draw face landmarks on a copy of the frame's image.

    Draws contours by default rather than the full 2556-connection tesselation,
    which buries the irises. The face mesh is drawn as connections only, with no
    dot per landmark: at 478 points the dots are the picture.

    Args:
        frame: Source frame.
        detection_result: Face detection result.
        face_idx: Which detected face to draw (default first).
        mesh: ``contours`` for the readable outline, ``tesselation`` for the
            full mesh.
        draw_irises: Also draw the two iris rings.

    Returns:
        Annotated RGB numpy array.
    """
    rgb_image = np.copy(frame.image.numpy_view())

    face_landmarks = get_landmarks_from_result(
        detection_result, "normalized", idx=face_idx
    )
    if face_landmarks is None:
        lg.warning("No face landmarks detected.")
        return rgb_image

    if mesh == "tesselation":
        connections = get_face_tesselation_connections()
        style = mp_drawing_styles.get_default_face_mesh_tesselation_style()
    else:
        connections = get_default_face_connections()
        style = mp_drawing_styles.get_default_face_mesh_contours_style()

    mp_drawing_utils.draw_landmarks(
        rgb_image,
        face_landmarks,
        connections,
        None,
        style,
    )

    if draw_irises:
        mp_drawing_utils.draw_landmarks(
            rgb_image,
            face_landmarks,
            get_face_iris_connections(),
            None,
            mp_drawing_styles.get_default_face_mesh_iris_connections_style(),
        )

    return rgb_image
