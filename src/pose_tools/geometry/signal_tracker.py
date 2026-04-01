"""Signal processing for gesture detection.

Layer on top of ``pose_tools.utils.np_signal`` providing stateful signal
tracking with smoothing, first/second derivative computation, and
threshold-based classification.

The ``SignalTracker`` is a generic version of holo-table's ``PinchTracker``
- it tracks any 1-D signal through a smooth-differentiate-classify pipeline.
Consumers can subclass or wrap it for specific gesture logic.
"""

import numpy as np

from pose_tools.utils.np_signal import create_left_triangle_filter
from pose_tools.utils.np_signal import roll_append_smooth


class SignalTracker:
    """Track a 1-D signal with smoothing and derivative-based classification.

    Maintains rolling history buffers for the raw signal, smoothed signal,
    first and second derivatives (each also smoothed).  On each ``update()``,
    classifies whether the current signal meets the derivative thresholds.

    Args:
        sd_max: Maximum absolute first derivative for a positive classification.
        sd_min: Minimum absolute first derivative for a positive classification.
        sdsd_max: Maximum absolute second derivative for a positive classification.
        filter_size: Rolling window size for the triangle filter.
    """

    def __init__(
        self,
        sd_max: float,
        sd_min: float,
        sdsd_max: float,
        filter_size: int = 5,
    ) -> None:
        """Initialize the tracker.

        Args:
            sd_max: Maximum first derivative for a positive classification.
            sd_min: Minimum first derivative for a positive classification.
            sdsd_max: Maximum absolute second derivative.
            filter_size: Rolling window size for the triangle filter.
        """
        self.sd_max = sd_max
        self.sd_min = sd_min
        self.sdsd_max = sdsd_max

        self.filter_size = filter_size
        self.filt = create_left_triangle_filter(self.filter_size)

        self.h_value = np.zeros(self.filter_size, dtype=float)
        self.h_value_s = np.zeros(self.filter_size, dtype=float)

        self.h_sd = np.zeros(self.filter_size, dtype=float)
        self.h_sds = np.zeros(self.filter_size, dtype=float)

        self.h_sdsd = np.zeros(self.filter_size, dtype=float)
        self.h_sdsds = np.zeros(self.filter_size, dtype=float)

        self.is_active: bool = False
        self.is_active_sd: bool = False
        self.is_active_sdsd: bool = False

        self.all_values: list[float] = []
        self.all_values_s: list[float] = []
        self.all_sd: list[float] = []
        self.all_sds: list[float] = []
        self.all_sdsd: list[float] = []
        self.all_sdsds: list[float] = []
        self.all_is_active: list[bool] = []

    def update(self, value: float) -> float:
        """Feed a new sample and update the classification state.

        Args:
            value: New raw signal value.

        Returns:
            The doubly-smoothed first derivative if active, else 0.
        """
        self.h_value, self.h_value_s = roll_append_smooth(
            self.h_value, self.h_value_s, value, self.filt
        )

        sd = float(self.h_value_s[-1] - self.h_value_s[-2])
        self.h_sd, self.h_sds = roll_append_smooth(self.h_sd, self.h_sds, sd, self.filt)

        sdsd = float(self.h_sds[-1] - self.h_sds[-2])
        self.h_sdsd, self.h_sdsds = roll_append_smooth(
            self.h_sdsd, self.h_sdsds, sdsd, self.filt
        )

        a_sds = np.abs(self.h_sds)
        a_sdsds = np.abs(self.h_sdsds)

        self.is_active_sd = bool(
            np.all(a_sds > self.sd_min) and np.all(a_sds < self.sd_max)
        )
        self.is_active_sdsd = bool(np.all(a_sdsds < self.sdsd_max))
        self.is_active = self.is_active_sd and self.is_active_sdsd

        rate = float(np.dot(self.h_sds, self.filt))

        self.all_values.append(value)
        self.all_values_s.append(float(self.h_value_s[-1]))
        self.all_sd.append(sd)
        self.all_sds.append(float(self.h_sds[-1]))
        self.all_sdsd.append(sdsd)
        self.all_sdsds.append(float(self.h_sdsds[-1]))
        self.all_is_active.append(self.is_active)

        return rate if self.is_active else 0.0
