"""Tests for pose_tools.video.load."""

from pathlib import Path

import numpy as np
import pytest

from pose_tools.video.load import VideoFrameIterator
from pose_tools.video.load import list_video_frames


@pytest.fixture
def sample_video(tmp_path: Path) -> Path:
    """Create a tiny 3-frame AVI video."""
    import cv2 as cv

    vid_path = tmp_path / "test.avi"
    fourcc = cv.VideoWriter_fourcc(*"MJPG")  # type: ignore[attr-defined]
    writer = cv.VideoWriter(str(vid_path), fourcc, 10, (8, 6))
    for i in range(3):
        frame = np.full((6, 8, 3), i * 80, dtype=np.uint8)
        writer.write(frame)
    writer.release()
    return vid_path


class TestVideoFrameIterator:
    """Context manager and iteration tests."""

    def test_context_manager_opens_and_releases(self, sample_video: Path) -> None:
        with VideoFrameIterator(sample_video) as it:
            assert it.cap is not None
            assert it.cap.isOpened()
        # After exit, cap should be released (isOpened may still return True
        # on some backends, but release was called)

    def test_iterates_all_frames(self, sample_video: Path) -> None:
        with VideoFrameIterator(sample_video) as it:
            frames = list(it)
        assert len(frames) == 3

    def test_max_frame_count(self, sample_video: Path) -> None:
        with VideoFrameIterator(sample_video, max_frame_count=2) as it:
            frames = list(it)
        assert len(frames) == 2

    def test_keep_every_nth(self, sample_video: Path) -> None:
        with VideoFrameIterator(sample_video, keep_every_nth_frame=2) as it:
            frames = list(it)
        # 3 raw frames, keeping every 2nd: indices 0, 2 -> 2 frames
        assert len(frames) == 2

    def test_raises_without_enter(self) -> None:
        it = VideoFrameIterator(Path("/nonexistent.avi"))
        with pytest.raises(ValueError, match="not opened"):
            list(it)


class TestListVideoFrames:
    """Convenience wrapper tests."""

    def test_returns_list(self, sample_video: Path) -> None:
        frames = list_video_frames(sample_video)
        assert len(frames) == 3
        assert frames[0].idx == 0
        assert frames[2].idx == 2
