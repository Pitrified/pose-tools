"""Base landmarker pattern for MediaPipe Tasks API wrappers.

Defines the common interface, mode-dispatch logic and lifecycle shared by both
``PoseLandmarkerFrame`` and ``HandLandmarkerFrame``.
"""

from types import TracebackType
from typing import Self

from loguru import logger as lg
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode as VisionRunningMode,
)

from pose_tools.video.frame import Frame


class LandmarkerClosedError(RuntimeError):
    """Raised when a landmarker is used after it has been closed."""

    def __init__(self, class_name: str) -> None:
        """Initialise with the name of the closed landmarker class.

        Args:
            class_name: Name of the landmarker class that was already closed.
        """
        super().__init__(f"{class_name} is closed, create a new one to detect again")


class BaseLandmarkerFrame[ResultT]:
    """Base class for landmarkers that accept ``Frame`` objects.

    Subclasses must set ``self._landmarker`` (the MediaPipe task object)
    and ``self._running_mode`` during ``__init__``.

    The underlying MediaPipe task holds native resources. Release them with
    ``close()``, or use the landmarker as a context manager::

        with PoseLandmarkerFrame(model_path) as plf:
            result = plf.detect(frame)

    Without that, the task is only released when the garbage collector reaches
    it, which at interpreter shutdown can surface as a spurious error from
    MediaPipe's own ``__del__``.
    """

    _landmarker: object
    _running_mode: VisionRunningMode
    _closed: bool = False

    def detect(self, frame: Frame) -> ResultT:
        """Detect landmarks in a frame, dispatching on running mode.

        Args:
            frame: Input video frame.

        Returns:
            Detection result (type depends on the concrete landmarker).

        Raises:
            LandmarkerClosedError: If the landmarker has already been closed.
        """
        if self._closed:
            raise LandmarkerClosedError(type(self).__name__)
        if self._running_mode == VisionRunningMode.IMAGE:
            return self._landmarker.detect(frame.image)  # type: ignore[union-attr]
        return self._landmarker.detect_for_video(frame.image, int(frame.msec))  # type: ignore[union-attr]

    def close(self) -> None:
        """Release the underlying MediaPipe task.

        Idempotent: closing an already closed landmarker does nothing.
        """
        if self._closed:
            return
        self._closed = True
        lg.debug(f"Closing {type(self).__name__}")
        self._landmarker.close()  # type: ignore[attr-defined]

    def __enter__(self) -> Self:
        """Return the landmarker for use in a ``with`` block."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the landmarker on leaving the ``with`` block."""
        self.close()
