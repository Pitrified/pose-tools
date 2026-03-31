"""Test the pose_tools paths."""

from pose_tools.params.pose_tools_params import get_pose_tools_paths


def test_pose_tools_paths() -> None:
    """Test the pose_tools paths."""
    pose_tools_paths = get_pose_tools_paths()
    assert pose_tools_paths.src_fol.name == "pose_tools"
    assert pose_tools_paths.root_fol.name == "pose-tools"
    assert pose_tools_paths.data_fol.name == "data"
