"""A frame is a video frame with a timestamp and an index.

Wraps a MediaPipe Image for interoperability with the MediaPipe Tasks API.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

import cv2 as cv
import mediapipe as mp
from mediapipe import Image
import numpy as np


@dataclass
class Frame:
    """A video frame backed by a MediaPipe Image.

    The underlying ``image`` stores pixel data in RGB format.

    Args:
        image: MediaPipe Image (RGB).
        msec: Timestamp in milliseconds.
        idx: Frame index.
    """

    image: Image
    msec: float
    idx: int

    @property
    def usec(self) -> int:
        """Timestamp in microseconds (for backward compatibility)."""
        return int(self.msec * 1000)

    @classmethod
    def from_np_array(
        cls,
        array: np.ndarray,
        msec: float = 0,
        idx: int = 0,
    ) -> Self:
        """Create a frame from an RGB numpy array."""
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=array)
        return cls(image, msec, idx)

    @classmethod
    def from_opencv(
        cls,
        array: np.ndarray,
        msec: float = 0,
        idx: int = 0,
    ) -> Self:
        """Create a frame from a BGR OpenCV array."""
        rgb = cv.cvtColor(array, cv.COLOR_BGR2RGB)
        return cls.from_np_array(rgb, msec, idx)

    @classmethod
    def from_file(
        cls,
        image_path: Path,
        msec: float = 0,
        idx: int = 0,
    ) -> Self:
        """Create a frame from an image file."""
        image = mp.Image.create_from_file(str(image_path))
        return cls(image, msec, idx)

    def to_numpy(self) -> np.ndarray:
        """Return the raw RGB numpy array (read-only view)."""
        return self.image.numpy_view()

    def to_opencv(self) -> np.ndarray:
        """Return a BGR numpy array suitable for OpenCV."""
        return cv.cvtColor(self.to_numpy(), cv.COLOR_RGB2BGR)

    def __str__(self) -> str:
        """Return the string representation of a frame."""
        return f"Frame(idx={self.idx}, msec={self.msec:.3f})"

    def __repr__(self) -> str:
        """Return a detailed string representation of a frame."""
        return str(self)
