"""Base landmarker pattern for MediaPipe Tasks API wrappers.

Defines the common interface and mode-dispatch logic shared by both
``PoseLandmarkerFrame`` and ``HandLandmarkerFrame``.
"""

from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode as VisionRunningMode,
)

from pose_tools.video.frame import Frame


class BaseLandmarkerFrame[ResultT]:
    """Base class for landmarkers that accept ``Frame`` objects.

    Subclasses must set ``self._landmarker`` (the MediaPipe task object)
    and ``self._running_mode`` during ``__init__``.
    """

    _landmarker: object
    _running_mode: VisionRunningMode

    def detect(self, frame: Frame) -> ResultT:
        """Detect landmarks in a frame, dispatching on running mode.

        Args:
            frame: Input video frame.

        Returns:
            Detection result (type depends on the concrete landmarker).
        """
        if self._running_mode == VisionRunningMode.IMAGE:
            return self._landmarker.detect(frame.image)  # type: ignore[union-attr]
        return self._landmarker.detect_for_video(frame.image, int(frame.msec))  # type: ignore[union-attr]
