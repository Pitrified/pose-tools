"""Test the PoseToolsParams class."""

from pose_tools.params.pose_tools_params import PoseToolsParams
from pose_tools.params.pose_tools_params import get_pose_tools_params
from pose_tools.params.pose_tools_paths import PoseToolsPaths


def test_pose_tools_params_singleton() -> None:
    """Test that PoseToolsParams is a singleton."""
    params1 = PoseToolsParams()
    params2 = PoseToolsParams()
    assert params1 is params2
    assert get_pose_tools_params() is params1


def test_pose_tools_params_init() -> None:
    """Test initialization of PoseToolsParams."""
    params = PoseToolsParams()
    assert isinstance(params.paths, PoseToolsPaths)


def test_pose_tools_params_str() -> None:
    """Test string representation."""
    params = PoseToolsParams()
    s = str(params)
    assert "PoseToolsParams:" in s
    assert "PoseToolsPaths:" in s
