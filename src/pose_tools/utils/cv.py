"""OpenCV display and image utilities."""

import math

import cv2 as cv
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np


def resize(
    image: np.ndarray,
    desired_width: int = 640,
    desired_height: int = 480,
) -> np.ndarray:
    """Resize an image preserving aspect ratio.

    The image is scaled so its larger dimension fits within the desired
    bounds, and the other dimension is scaled proportionally.

    Args:
        image: Input image (any channel count).
        desired_width: Target width when the image is wider than tall.
        desired_height: Target height when the image is taller than wide.
    """
    h, w = image.shape[:2]
    if h < w:
        new_w = desired_width
        new_h = math.floor(h / (w / desired_width))
    else:
        new_h = desired_height
        new_w = math.floor(w / (h / desired_height))
    return cv.resize(image, (new_w, new_h))


def cv_imshow(
    img: np.ndarray,
    ax: Axes | None = None,
) -> None:
    """Display a BGR image in a matplotlib figure.

    Args:
        img: BGR numpy array.
        ax: Optional axes to draw on.  If ``None``, a new figure is created
            and ``plt.show()`` is called.
    """
    rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    if ax is not None:
        ax.imshow(rgb)
        return
    fig, new_ax = plt.subplots(1, 1)
    new_ax.imshow(rgb)
    plt.show()
    plt.close(fig)


def cv_imshow_rgb(winname: str, image_rgb: np.ndarray) -> None:
    """Show an RGB image in an OpenCV ``imshow`` window.

    Args:
        winname: Window name.
        image_rgb: RGB numpy array.
    """
    image_bgr = cv.cvtColor(image_rgb, cv.COLOR_RGB2BGR)
    cv.imshow(winname, image_bgr)
