"""PoseTools project params.

Parameters are actual value of the config.

The class is a singleton, so it can be accessed from anywhere in the code.

There is a parameter regarding the environment type (stage and location), which
is used to load different paths and other parameters based on the environment.
"""

from loguru import logger as lg

from pose_tools.metaclasses.singleton import Singleton
from pose_tools.params.env_type import EnvType
from pose_tools.params.pose_tools_paths import PoseToolsPaths
from pose_tools.params.sample_params import SampleParams


class PoseToolsParams(metaclass=Singleton):
    """PoseTools project parameters."""

    def __init__(self) -> None:
        """Load the PoseTools params."""
        lg.info("Loading PoseTools params")
        self.set_env_type()

    def set_env_type(self, env_type: EnvType | None = None) -> None:
        """Set the environment type.

        Args:
            env_type (EnvType | None): The environment type.
                If None, it will be set from the environment variables.
                Defaults to None.
        """
        if env_type is not None:
            self.env_type = env_type
        else:
            self.env_type = EnvType.from_env_var()
        self.load_config()

    def load_config(self) -> None:
        """Load the pose_tools configuration."""
        self.paths = PoseToolsPaths(env_type=self.env_type)
        self.sample = SampleParams()

    def __str__(self) -> str:
        """Return the string representation of the object."""
        s = "PoseToolsParams:"
        s += f"\n{self.paths}"
        s += f"\n{self.sample}"
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
