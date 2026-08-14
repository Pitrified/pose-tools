"""Tests for the pose, hand and face landmarker wrappers.

The wrappers are thin subclasses of ``BaseLandmarkerFrame`` whose only real
work is reading ``running_mode`` out of the kwargs and building the native
task. Building the task needs a ``.task`` file, so the constructor is patched
out here and the rest is exercised for real - the same trade as
``test_base.py``, applied to all three concrete classes.
"""

from pathlib import Path
from typing import Any

from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode as VisionRunningMode,
)
import pytest

from pose_tools.landmark import face as face_mod
from pose_tools.landmark import hand as hand_mod
from pose_tools.landmark import pose as pose_mod
from pose_tools.landmark.base import BaseLandmarkerFrame
from pose_tools.landmark.base import LandmarkerClosedError
from pose_tools.landmark.face import FaceLandmarkerFrame
from pose_tools.landmark.hand import HandLandmarkerFrame
from pose_tools.landmark.pose import PoseLandmarkerFrame
from pose_tools.video.frame import Frame


class FakeTask:
    """Stand-in for a MediaPipe task object."""

    def __init__(self, model_path: Path, **kwargs: object) -> None:
        self.model_path = model_path
        self.kwargs = kwargs
        self.close_count = 0

    def detect(self, image: object) -> str:  # noqa: ARG002 - mirrors the MediaPipe signature
        return "image-result"

    def detect_for_video(self, image: object, timestamp_ms: int) -> str:  # noqa: ARG002 - same
        return f"video-result-{timestamp_ms}"

    def close(self) -> None:
        self.close_count += 1


class Wrapper:
    """A landmarker class with its native factory faked out.

    Holds the tasks the factory built, so the tests can assert on what reached
    MediaPipe without reading private attributes off the landmarker.
    """

    def __init__(self, cls: type, tasks: list[FakeTask]) -> None:
        self.cls = cls
        self.tasks = tasks

    def __call__(self, *args: object, **kwargs: object) -> BaseLandmarkerFrame:
        """Build a landmarker of the wrapped class."""
        return self.cls(*args, **kwargs)

    @property
    def task(self) -> FakeTask:
        """The task built most recently."""
        return self.tasks[-1]


# Each wrapper, paired with the module-level factory it calls.
WRAPPERS: list[tuple[str, type, Any, str]] = [
    ("pose", PoseLandmarkerFrame, pose_mod, "create_pose_landmarker"),
    ("hand", HandLandmarkerFrame, hand_mod, "create_hand_landmarker"),
    ("face", FaceLandmarkerFrame, face_mod, "create_face_landmarker"),
]
WRAPPER_IDS = [name for name, _, _, _ in WRAPPERS]


@pytest.fixture(params=WRAPPERS, ids=WRAPPER_IDS)
def wrapper(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> Wrapper:
    """Yield each landmarker class with its native factory faked out."""
    _, cls, module, factory_name = request.param
    tasks: list[FakeTask] = []

    def factory(model_path: Path, **kwargs: object) -> FakeTask:
        task = FakeTask(model_path, **kwargs)
        tasks.append(task)
        return task

    monkeypatch.setattr(module, factory_name, factory)
    return Wrapper(cls, tasks)


@pytest.fixture
def frame() -> Frame:
    """Build a frame carrying only what the dispatch logic reads."""
    return Frame(image=object(), msec=1234.0, idx=0)  # type: ignore[arg-type]


class TestConstruction:
    """What the wrappers pass on to MediaPipe."""

    def test_model_path_reaches_the_task(self, wrapper: Wrapper) -> None:
        wrapper(Path("some/model.task"))
        assert wrapper.task.model_path == Path("some/model.task")

    def test_extra_kwargs_are_forwarded(self, wrapper: Wrapper) -> None:
        wrapper(Path("model.task"), {"min_tracking_confidence": 0.9})
        assert wrapper.task.kwargs["min_tracking_confidence"] == 0.9

    def test_running_mode_is_forwarded_too(self, wrapper: Wrapper) -> None:
        wrapper(Path("model.task"), {"running_mode": VisionRunningMode.VIDEO})
        assert wrapper.task.kwargs["running_mode"] == VisionRunningMode.VIDEO


class TestLifecycle:
    """Detect dispatch, close and context manager, per concrete class."""

    def test_defaults_to_image_mode(self, wrapper: Wrapper, frame: Frame) -> None:
        assert wrapper(Path("model.task")).detect(frame) == "image-result"

    def test_video_mode_passes_the_timestamp(
        self, wrapper: Wrapper, frame: Frame
    ) -> None:
        lm = wrapper(Path("model.task"), {"running_mode": VisionRunningMode.VIDEO})
        assert lm.detect(frame) == "video-result-1234"

    def test_close_is_idempotent(self, wrapper: Wrapper) -> None:
        lm = wrapper(Path("model.task"))
        lm.close()
        lm.close()
        assert wrapper.task.close_count == 1

    def test_detect_after_close_raises(self, wrapper: Wrapper, frame: Frame) -> None:
        lm = wrapper(Path("model.task"))
        lm.close()
        with pytest.raises(LandmarkerClosedError):
            lm.detect(frame)

    def test_context_manager_closes(self, wrapper: Wrapper) -> None:
        with wrapper(Path("model.task")):
            assert wrapper.task.close_count == 0
        assert wrapper.task.close_count == 1
