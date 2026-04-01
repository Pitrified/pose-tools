"""Hand landmarker wrapper using the MediaPipe Tasks API."""

from pathlib import Path

from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode as VisionRunningMode,
)
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarker
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerOptions
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarkerResult

from pose_tools.landmark.base import BaseLandmarkerFrame
from pose_tools.video.frame import Frame


def create_hand_landmarker(
    model_path: Path,
    **kwargs: object,
) -> HandLandmarker:
    """Create a ``HandLandmarker`` from a ``.task`` model file.

    Extra *kwargs* are forwarded to ``HandLandmarkerOptions`` (e.g.
    ``running_mode``, ``num_hands``, ``min_hand_detection_confidence``).
    """
    base_options = BaseOptions(model_asset_path=str(model_path))
    options = HandLandmarkerOptions(base_options=base_options, **kwargs)  # type: ignore[arg-type]
    return HandLandmarker.create_from_options(options)


class HandLandmarkerFrame(BaseLandmarkerFrame[HandLandmarkerResult]):
    """Hand landmarker that accepts ``Frame`` objects as input.

    Args:
        model_path: Path to the ``hand_landmarker.task`` model file.
        landmarker_kwargs: Extra options forwarded to ``HandLandmarkerOptions``.
    """

    def __init__(
        self,
        model_path: Path,
        landmarker_kwargs: dict | None = None,
    ) -> None:
        """Initialize the hand landmarker.

        Args:
            model_path: Path to the ``hand_landmarker.task`` model file.
            landmarker_kwargs: Extra options forwarded to ``HandLandmarkerOptions``.
        """
        kw = landmarker_kwargs or {}
        self._running_mode = kw.get("running_mode", VisionRunningMode.IMAGE)  # type: ignore[assignment]
        self._landmarker = create_hand_landmarker(model_path, **kw)

    def detect(self, frame: Frame) -> HandLandmarkerResult:
        """Detect hand landmarks in a frame."""
        return super().detect(frame)
