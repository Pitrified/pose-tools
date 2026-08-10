"""Tests for the landmarker lifecycle in pose_tools.landmark.base."""

from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode as VisionRunningMode,
)
import pytest

from pose_tools.landmark.base import BaseLandmarkerFrame
from pose_tools.landmark.base import LandmarkerClosedError
from pose_tools.video.frame import Frame


class FakeTask:
    """Stand-in for a MediaPipe task object.

    The real one needs a ``.task`` model file on disk, which the test suite
    does not ship.
    """

    def __init__(self) -> None:
        self.close_count = 0
        self.detect_count = 0

    def detect(self, image: object) -> str:  # noqa: ARG002 - mirrors the MediaPipe signature
        self.detect_count += 1
        return "image-result"

    def detect_for_video(self, image: object, timestamp_ms: int) -> str:  # noqa: ARG002 - same
        self.detect_count += 1
        return f"video-result-{timestamp_ms}"

    def close(self) -> None:
        self.close_count += 1


class FakeLandmarker(BaseLandmarkerFrame[str]):
    """Concrete landmarker over ``FakeTask``."""

    def __init__(
        self, running_mode: VisionRunningMode = VisionRunningMode.IMAGE
    ) -> None:
        self._running_mode = running_mode
        self._landmarker = FakeTask()

    @property
    def task(self) -> FakeTask:
        """The fake task, typed for the assertions below."""
        return self._landmarker  # type: ignore[return-value]


@pytest.fixture
def frame() -> Frame:
    """Build a frame carrying only what the dispatch logic reads."""
    return Frame(image=object(), msec=1234.0, idx=0)  # type: ignore[arg-type]


class TestClose:
    """Releasing the underlying task."""

    def test_close_closes_the_task(self) -> None:
        lm = FakeLandmarker()
        lm.close()
        assert lm.task.close_count == 1

    def test_close_is_idempotent(self) -> None:
        lm = FakeLandmarker()
        lm.close()
        lm.close()
        assert lm.task.close_count == 1

    def test_detect_after_close_raises(self, frame: Frame) -> None:
        lm = FakeLandmarker()
        lm.close()
        with pytest.raises(LandmarkerClosedError):
            lm.detect(frame)

    def test_detect_works_before_close(self, frame: Frame) -> None:
        lm = FakeLandmarker()
        assert lm.detect(frame) == "image-result"


class TestContextManager:
    """Using the landmarker in a ``with`` block."""

    def test_closes_on_exit(self, frame: Frame) -> None:
        with FakeLandmarker() as lm:
            lm.detect(frame)
            task = lm.task
        assert task.close_count == 1

    def test_closes_when_the_body_raises(self) -> None:
        lm = FakeLandmarker()
        msg = "boom"
        with pytest.raises(ValueError, match=msg), lm:
            raise ValueError(msg)
        assert lm.task.close_count == 1

    def test_enter_returns_the_landmarker(self) -> None:
        lm = FakeLandmarker()
        with lm as entered:
            assert entered is lm


class TestRunningModeDispatch:
    """Which task method each running mode calls."""

    def test_image_mode_uses_detect(self, frame: Frame) -> None:
        lm = FakeLandmarker(VisionRunningMode.IMAGE)
        assert lm.detect(frame) == "image-result"

    def test_video_mode_passes_the_timestamp(self, frame: Frame) -> None:
        lm = FakeLandmarker(VisionRunningMode.VIDEO)
        assert lm.detect(frame) == "video-result-1234"
