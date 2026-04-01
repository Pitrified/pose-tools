"""Matplotlib plotting utilities for frames."""

from matplotlib.axes import Axes
import matplotlib.pyplot as plt

from pose_tools.utils.cv import resize
from pose_tools.video.frame import Frame


def show_frame(
    frame: Frame,
    ax: Axes | None = None,
    title_suffix: str | None = None,
    *,
    do_show: bool = True,
    do_resize: bool = True,
) -> None:
    """Display a ``Frame`` in a matplotlib axes.

    Args:
        frame: Frame to display.
        ax: Target axes. Created automatically when ``None``.
        title_suffix: Extra text appended to the title.
        do_show: Call ``plt.show()`` after rendering.
        do_resize: Resize the image before displaying.
    """
    if ax is None:
        _, ax = plt.subplots()

    img = resize(frame.image.numpy_view()) if do_resize else frame.image.numpy_view()
    ax.imshow(img)

    ax.set_axis_off()

    title = f"{frame.idx} @ {frame.msec:.0f}"
    if title_suffix is not None:
        title += f" {title_suffix}"
    ax.set_title(title)

    if do_show:
        plt.show()
