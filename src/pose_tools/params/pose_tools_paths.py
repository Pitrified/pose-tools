"""Paths and folders for data files."""

from pathlib import Path

import pose_tools
from pose_tools.params.env_type import EnvLocationType
from pose_tools.params.env_type import EnvType
from pose_tools.params.env_type import UnknownEnvLocationError


class PoseToolsPaths:
    """Paths and folders for data and resources."""

    def __init__(
        self,
        env_type: EnvType,
    ) -> None:
        """Load the config for data folders."""
        self.env_type = env_type
        self.load_config()

    def load_config(self) -> None:
        """Load the config for data folders."""
        self.load_common_config_pre()
        match self.env_type.location:
            case EnvLocationType.LOCAL:
                self.load_local_config()
            case EnvLocationType.RENDER:
                self.load_render_config()
            case _:
                raise UnknownEnvLocationError(self.env_type.location)

    def load_common_config_pre(self) -> None:
        """Pre load the common config."""
        # src folder of the package
        self.src_fol = Path(pose_tools.__file__).parent
        # root folder of the project repository
        self.root_fol = self.src_fol.parents[1]
        # cache
        self.cache_fol = self.root_fol / "cache"
        # data
        self.data_fol = self.root_fol / "data"

    def load_local_config(self) -> None:
        """Load the config for local environment."""

    def load_render_config(self) -> None:
        """Load the config for Render environment."""

    def __str__(self) -> str:
        """Return the string representation of the object."""
        s = "PoseToolsPaths:\n"
        s += f"      src_fol: {self.src_fol}\n"
        s += f"     root_fol: {self.root_fol}\n"
        s += f"    cache_fol: {self.cache_fol}\n"
        s += f"     data_fol: {self.data_fol}\n"
        return s.rstrip()
