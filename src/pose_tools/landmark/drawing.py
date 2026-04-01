"""Drawing utilities for pose and hand landmarks."""

from loguru import logger as lg
from mediapipe.tasks.python.vision import drawing_styles as mp_drawing_styles
from mediapipe.tasks.python.vision import drawing_utils as mp_drawing_utils
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerResult
import numpy as np

from pose_tools.utils.mediapipe import get_default_hand_connections
from pose_tools.utils.mediapipe import get_default_pose_connections
from pose_tools.utils.mediapipe import get_landmarks_from_result
from pose_tools.video.frame import Frame


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
