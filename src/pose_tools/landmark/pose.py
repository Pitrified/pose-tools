"""Pose landmarker wrapper using the MediaPipe Tasks API."""

from pathlib import Path

from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode as VisionRunningMode,
)
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarker
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerOptions
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerResult

from pose_tools.landmark.base import BaseLandmarkerFrame
from pose_tools.video.frame import Frame


def create_pose_landmarker(
    model_path: Path,
    **kwargs: object,
) -> PoseLandmarker:
    """Create a ``PoseLandmarker`` from a ``.task`` model file.

    Extra *kwargs* are forwarded to ``PoseLandmarkerOptions`` (e.g.
    ``running_mode``, ``num_poses``, ``min_pose_detection_confidence``).
    """
    base_options = BaseOptions(model_asset_path=str(model_path))
    options = PoseLandmarkerOptions(base_options=base_options, **kwargs)  # type: ignore[arg-type]
    return PoseLandmarker.create_from_options(options)


class PoseLandmarkerFrame(BaseLandmarkerFrame[PoseLandmarkerResult]):
    """Pose landmarker that accepts ``Frame`` objects as input.

    Args:
        model_path: Path to the ``pose_landmarker.task`` model file.
        landmarker_kwargs: Extra options forwarded to ``PoseLandmarkerOptions``.
    """

    def __init__(
        self,
        model_path: Path,
        landmarker_kwargs: dict | None = None,
    ) -> None:
        """Initialize the pose landmarker.

        Args:
            model_path: Path to the ``pose_landmarker.task`` model file.
            landmarker_kwargs: Extra options forwarded to ``PoseLandmarkerOptions``.
        """
        kw = landmarker_kwargs or {}
        self._running_mode = kw.get("running_mode", VisionRunningMode.IMAGE)  # type: ignore[assignment]
        self._landmarker = create_pose_landmarker(model_path, **kw)

    def detect(self, frame: Frame) -> PoseLandmarkerResult:
        """Detect pose landmarks in a frame."""
        return super().detect(frame)
