"""Numpy signal processing utilities.

General-purpose rolling window filters, derivatives, and smoothing
functions useful for gesture tracking pipelines.
"""

import numpy as np


def diff_pad(x: np.ndarray) -> np.ndarray:
    """Compute differences between adjacent elements, padding the first.

    The first element is kept unchanged (prepended before diff).
    """
    return np.diff(x, prepend=x[0])


def create_left_triangle_filter(window_size: int) -> np.ndarray:
    """Create a left-aligned triangular smoothing filter.

    The filter has linearly increasing weights that sum to 1.

    Args:
        window_size: Number of taps.
    """
    triangle = np.arange(1, window_size + 1, dtype=float)
    triangle /= triangle.sum()
    return triangle


def roll_append(x: np.ndarray, val: float) -> np.ndarray:
    """Roll array left by one and assign *val* at the end.

    Args:
        x: 1-D array.
        val: Value to append.
    """
    x = np.roll(x, -1)
    x[-1] = val
    return x


def roll_append_smooth(
    hist: np.ndarray,
    hist_smooth: np.ndarray,
    value: float,
    filt: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Append a value, smooth with *filt*, and update the smoothed history.

    Args:
        hist: Raw history array (same length as *filt*).
        hist_smooth: Smoothed history array.
        value: New raw value to append.
        filt: Smoothing filter (e.g., from ``create_left_triangle_filter``).

    Returns:
        Updated ``(hist, hist_smooth)`` tuple.
    """
    hist = roll_append(hist, value)
    value_smooth = np.dot(hist, filt)
    hist_smooth = roll_append(hist_smooth, value_smooth)
    return hist, hist_smooth
