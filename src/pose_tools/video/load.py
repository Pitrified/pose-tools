"""Load video frames from a file or camera.

Provides a context-managed iterator (``VideoFrameIterator``) and convenience
wrappers for common access patterns.
"""

from collections.abc import Generator
from pathlib import Path
from typing import Self

import cv2 as cv
from loguru import logger as lg

from pose_tools.video.frame import Frame


class VideoFrameIterator:
    """Context-managed video frame iterator.

    Args:
        in_vid_path: Input video file. ``None`` opens the default camera.
        keep_every_nth_frame: Keep every *n*-th frame.
        max_frame_count: Maximum frames to yield (0 = unlimited).
    """

    def __init__(
        self,
        in_vid_path: Path | None = None,
        keep_every_nth_frame: int = 1,
        max_frame_count: int = 0,
    ) -> None:
        """Initialize the iterator.

        Args:
            in_vid_path: Path to the video file.
            keep_every_nth_frame: Keep every *n*-th frame.
            max_frame_count: Maximum frames to yield (0 = unlimited).
        """
        self.in_vid_path = in_vid_path
        self.keep_every_nth_frame = keep_every_nth_frame
        self.max_frame_count = max_frame_count
        self.cap: cv.VideoCapture | None = None
        self.feed_count = 0
        self.yield_count = 0

    def __iter__(self) -> Generator[Frame]:
        """Yield frames from the opened video capture."""
        if self.cap is None:
            msg = "Video file or camera feed not opened."
            raise ValueError(msg)

        success = True
        while success and (
            self.max_frame_count == 0 or self.yield_count < self.max_frame_count
        ):
            success, frame = self.cap.read()
            if not success:
                break

            pos_msec = self.cap.get(cv.CAP_PROP_POS_MSEC)

            if self.feed_count % self.keep_every_nth_frame == 0:
                lg.debug(f"Yielding frame {self.yield_count} at {pos_msec:.2f} ms")
                yield Frame.from_opencv(frame, pos_msec, self.yield_count)
                self.yield_count += 1

            self.feed_count += 1

    def __enter__(self) -> Self:
        """Open the video file or camera feed."""
        if self.in_vid_path is None:
            self.cap = cv.VideoCapture(0)
        else:
            self.cap = cv.VideoCapture(str(self.in_vid_path))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        """Release the video capture."""
        if self.cap is not None:
            lg.debug("Releasing video capture")
            self.cap.release()


def list_video_frames(
    in_vid_path: Path,
    keep_every_nth_frame: int = 1,
    max_frame_count: int = 0,
) -> list[Frame]:
    """Load frames from a video file into a list.

    Args:
        in_vid_path: Input video file.
        keep_every_nth_frame: Keep every *n*-th frame.
        max_frame_count: Maximum frames to return (0 = all).
    """
    with VideoFrameIterator(
        in_vid_path,
        keep_every_nth_frame=keep_every_nth_frame,
        max_frame_count=max_frame_count,
    ) as it:
        return list(it)


def iterate_video_frames(
    in_vid_path: Path,
    keep_every_nth_frame: int = 1,
) -> Generator[Frame]:
    """Iterate over frames from a video file.

    Thin wrapper around ``VideoFrameIterator`` for simple streaming use.

    Args:
        in_vid_path: Input video file.
        keep_every_nth_frame: Keep every *n*-th frame.
    """
    with VideoFrameIterator(
        in_vid_path,
        keep_every_nth_frame=keep_every_nth_frame,
    ) as it:
        yield from it
