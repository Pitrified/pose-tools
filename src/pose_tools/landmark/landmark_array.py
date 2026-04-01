"""Numpy-based landmark array with visibility masking and pixel coordinates.

Modernized from ``climbing-wire``'s ``LandmarkListNp`` / ``LandmarkListImg``
to work with the MediaPipe Tasks API landmark containers.
"""

from typing import Literal
from typing import Self

import numpy as np

from pose_tools.utils.mediapipe import POSE_LANDMARK_MAP
from pose_tools.utils.mediapipe import POSE_LANDMARK_NAMES
from pose_tools.utils.mediapipe import are_valid_normalized_points
from pose_tools.utils.mediapipe import normalized_to_pixel_coordinates


class LandmarkArray:
    """Pose landmarks stored as numpy arrays.

    Holds normalized (x, y) positions and per-landmark visibility scores.

    Args:
        landmarks_norm: Array of shape ``(N, 2)`` with normalized coordinates.
        visibility: Array of shape ``(N,)`` with visibility scores.
    """

    def __init__(
        self,
        landmarks_norm: np.ndarray,
        visibility: np.ndarray,
    ) -> None:
        """Initialize the landmark array.

        Args:
            landmarks_norm: Array of shape ``(N, 2)`` with normalized coordinates.
            visibility: Array of shape ``(N,)`` with visibility scores.
        """
        self.landmarks_norm = landmarks_norm
        self.visibility = visibility

    @classmethod
    def from_normalized_landmarks(
        cls,
        landmarks: list,
    ) -> Self:
        """Create from a Tasks API ``list[NormalizedLandmark]``.

        Each landmark must have ``.x``, ``.y``, and ``.visibility`` attributes.
        """
        norm_ls: list[tuple[float, float]] = []
        vis_ls: list[float] = []
        for lm in landmarks:
            norm_ls.append((lm.x, lm.y))
            vis_ls.append(lm.visibility)
        return cls(
            landmarks_norm=np.array(norm_ls),
            visibility=np.array(vis_ls),
        )

    def __len__(self) -> int:
        """Return the number of landmarks."""
        return len(self.landmarks_norm)

    def __repr__(self) -> str:
        """Pretty-print landmark positions."""
        lines: list[str] = []
        names = POSE_LANDMARK_NAMES if len(self) == len(POSE_LANDMARK_NAMES) else None
        for i, (pos, vis) in enumerate(
            zip(self.landmarks_norm, self.visibility, strict=True)
        ):
            name = names[i] if names else str(i)
            lines.append(f"{name:>19s} {pos[0]:.3f} {pos[1]:.3f} v={vis:.3f}")
        return "\n".join(lines)


class LandmarkArrayImg(LandmarkArray):
    """Landmark array extended with pixel coordinates and drawable flags.

    Args:
        landmarks_norm: Array of shape ``(N, 2)`` with normalized coordinates.
        visibility: Array of shape ``(N,)`` with visibility scores.
        image_size: ``(height, width)`` of the source image.
        visibility_threshold: Minimum visibility to consider a landmark drawable.
    """

    def __init__(
        self,
        landmarks_norm: np.ndarray,
        visibility: np.ndarray,
        image_size: tuple[int, int],
        visibility_threshold: float = 0.5,
    ) -> None:
        """Initialize the image landmark array.

        Args:
            landmarks_norm: Array of shape ``(N, 2)`` with normalized coordinates.
            visibility: Array of shape ``(N,)`` with visibility scores.
            image_size: ``(height, width)`` of the source image.
            visibility_threshold: Minimum visibility to consider drawable.
        """
        super().__init__(landmarks_norm, visibility)
        self.image_size = image_size
        self.visibility_threshold = visibility_threshold

        self.landmarks_img = normalized_to_pixel_coordinates(
            self.landmarks_norm, self.image_size
        )

        self.drawable = self.visibility > self.visibility_threshold
        self.drawable &= are_valid_normalized_points(self.landmarks_norm)

    @classmethod
    def from_normalized_landmarks(  # type: ignore[override]
        cls,
        landmarks: list,
        image_size: tuple[int, int] = (480, 640),
        visibility_threshold: float = 0.5,
    ) -> Self:
        """Create from a Tasks API ``list[NormalizedLandmark]``.

        Args:
            landmarks: List of landmarks with ``.x``, ``.y``, ``.visibility``.
            image_size: ``(height, width)`` of the source image.
            visibility_threshold: Minimum visibility to consider drawable.
        """
        norm_ls: list[tuple[float, float]] = []
        vis_ls: list[float] = []
        for lm in landmarks:
            norm_ls.append((lm.x, lm.y))
            vis_ls.append(lm.visibility)
        return cls(
            landmarks_norm=np.array(norm_ls),
            visibility=np.array(vis_ls),
            image_size=image_size,
            visibility_threshold=visibility_threshold,
        )

    def get_landmark_for_joint(
        self,
        which_landmark: Literal[
            "left_hand",
            "right_hand",
            "left_foot",
            "right_foot",
        ],
    ) -> tuple[np.ndarray, float]:
        """Get pixel position and visibility for a named joint.

        Args:
            which_landmark: Joint name.

        Returns:
            Tuple of ``(position_array_1x2, visibility_float)``.
        """
        joint_to_landmark = {
            "left_hand": "LEFT_WRIST",
            "right_hand": "RIGHT_WRIST",
            "left_foot": "LEFT_ANKLE",
            "right_foot": "RIGHT_ANKLE",
        }
        land_idx = int(POSE_LANDMARK_MAP[joint_to_landmark[which_landmark]])
        return (
            self.landmarks_img[land_idx : land_idx + 1, :],
            float(self.visibility[land_idx]),
        )

    def __repr__(self) -> str:
        """Pretty-print landmark pixel positions with drawable status."""
        lines: list[str] = []
        names = POSE_LANDMARK_NAMES if len(self) == len(POSE_LANDMARK_NAMES) else None
        for i, (pos, vis, draw) in enumerate(
            zip(self.landmarks_img, self.visibility, self.drawable, strict=True)
        ):
            name = names[i] if names else str(i)
            lines.append(f"{name:>19s} {pos} v={vis:.3f} d={draw}")
        return "\n".join(lines)

    def __str__(self) -> str:
        """Summary of drawable landmarks."""
        return (
            f"{self.__class__.__name__}"
            f"({self.drawable.sum()}/{len(self.drawable)} drawable)"
        )

    def copy(self) -> Self:
        """Return a copy of this landmark array."""
        return type(self)(
            landmarks_norm=self.landmarks_norm.copy(),
            visibility=self.visibility.copy(),
            image_size=self.image_size,
            visibility_threshold=self.visibility_threshold,
        )
