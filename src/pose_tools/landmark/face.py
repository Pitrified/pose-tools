"""Face landmarker wrapper using the MediaPipe Tasks API."""

from pathlib import Path

from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode as VisionRunningMode,
)
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarker
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarkerOptions
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarkerResult

from pose_tools.landmark.base import BaseLandmarkerFrame
from pose_tools.video.frame import Frame


def create_face_landmarker(
    model_path: Path,
    **kwargs: object,
) -> FaceLandmarker:
    """Create a ``FaceLandmarker`` from a ``.task`` model file.

    Extra *kwargs* are forwarded to ``FaceLandmarkerOptions`` (e.g.
    ``running_mode``, ``num_faces``, ``output_facial_transformation_matrixes``,
    ``output_face_blendshapes``).
    """
    base_options = BaseOptions(model_asset_path=str(model_path))
    options = FaceLandmarkerOptions(base_options=base_options, **kwargs)  # type: ignore[arg-type]
    return FaceLandmarker.create_from_options(options)


class FaceLandmarkerFrame(BaseLandmarkerFrame[FaceLandmarkerResult]):
    """Face landmarker that accepts ``Frame`` objects as input.

    Detects 478 landmarks per face, the last ten of which are the irises.
    ``facial_transformation_matrixes`` and ``face_blendshapes`` are off by
    default, as in MediaPipe: pass the matching option to switch them on.

    Args:
        model_path: Path to the ``face_landmarker.task`` model file.
        landmarker_kwargs: Extra options forwarded to ``FaceLandmarkerOptions``.
    """

    def __init__(
        self,
        model_path: Path,
        landmarker_kwargs: dict | None = None,
    ) -> None:
        """Initialize the face landmarker.

        Args:
            model_path: Path to the ``face_landmarker.task`` model file.
            landmarker_kwargs: Extra options forwarded to ``FaceLandmarkerOptions``.
        """
        kw = landmarker_kwargs or {}
        self._running_mode = kw.get("running_mode", VisionRunningMode.IMAGE)  # type: ignore[assignment]
        self._landmarker = create_face_landmarker(model_path, **kw)

    def detect(self, frame: Frame) -> FaceLandmarkerResult:
        """Detect face landmarks in a frame."""
        return super().detect(frame)
