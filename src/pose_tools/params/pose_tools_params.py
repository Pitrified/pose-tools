"""PoseTools project params.

Parameters are the actual values of the config.

The class is a singleton, so it can be accessed from anywhere in the code.
"""

from loguru import logger as lg

from pose_tools.metaclasses.singleton import Singleton
from pose_tools.params.pose_tools_paths import PoseToolsPaths


class PoseToolsParams(metaclass=Singleton):
    """PoseTools project parameters."""

    def __init__(self) -> None:
        """Load the PoseTools params."""
        lg.info("Loading PoseTools params")
        self.load_config()

    def load_config(self) -> None:
        """Load the pose_tools configuration."""
        self.paths = PoseToolsPaths()

    def __str__(self) -> str:
        """Return the string representation of the object."""
        s = "PoseToolsParams:"
        s += f"\n{self.paths}"
        return s

    def __repr__(self) -> str:
        """Return the string representation of the object."""
        return str(self)


def get_pose_tools_params() -> PoseToolsParams:
    """Get the pose_tools params."""
    return PoseToolsParams()


def get_pose_tools_paths() -> PoseToolsPaths:
    """Get the pose_tools paths."""
    return get_pose_tools_params().paths
