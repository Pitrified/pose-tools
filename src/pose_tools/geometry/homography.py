"""SIFT-based homography computation for camera motion compensation.

Uses SIFT feature detection, FLANN matching, and RANSAC to compute
the 3x3 homography matrix between two images.
"""

import cv2 as cv
import numpy as np

MIN_MATCH_COUNT = 10
LOWE_RATIO = 0.7


class InsufficientMatchesError(Exception):
    """Raised when too few feature matches are found for homography."""


def compute_homography(
    img1: np.ndarray,
    img2: np.ndarray,
    min_match_count: int = MIN_MATCH_COUNT,
) -> np.ndarray:
    """Compute the homography matrix warping *img1* onto *img2*.

    Both images are expected in BGR format (OpenCV convention).

    Args:
        img1: First image (BGR numpy array).
        img2: Second image (BGR numpy array).
        min_match_count: Minimum good matches required.

    Returns:
        3x3 homography matrix.

    Raises:
        InsufficientMatchesError: If fewer than *min_match_count* feature
            matches pass Lowe's ratio test.
    """
    gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
    gray2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)

    sift = cv.SIFT_create()  # type: ignore[attr-defined]
    kp1, des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)

    flann_index_kdtree = 1
    index_params = {"algorithm": flann_index_kdtree, "trees": 5}
    search_params = {"checks": 50}
    flann = cv.FlannBasedMatcher(index_params, search_params)  # type: ignore[arg-type]
    matches = flann.knnMatch(des1, des2, k=2)

    good = [m for m, n in matches if m.distance < LOWE_RATIO * n.distance]

    if len(good) < min_match_count:
        msg = (
            f"Not enough matches: {len(good)}/{min_match_count}. "
            f"Consider lowering min_match_count or using a different matcher."
        )
        raise InsufficientMatchesError(msg)

    src_pts = np.array([kp1[m.queryIdx].pt for m in good], dtype=np.float32).reshape(
        -1, 1, 2
    )
    dst_pts = np.array([kp2[m.trainIdx].pt for m in good], dtype=np.float32).reshape(
        -1, 1, 2
    )

    homography_matrix, _ = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
    return homography_matrix


def perspective_transform(
    points: np.ndarray,
    matrix: np.ndarray,
) -> np.ndarray:
    """Apply a 3x3 transformation matrix to a set of 2D points.

    Args:
        points: Array of shape ``(N, 2)``.
        matrix: 3x3 transformation (homography) matrix.

    Returns:
        Transformed points of shape ``(N, 2)``.
    """
    if len(points) == 0:
        return points
    pts = points.reshape(-1, 1, 2).astype(np.float64)
    transformed = cv.perspectiveTransform(pts, matrix)
    return transformed.reshape(-1, 2)
