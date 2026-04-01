"""Tests for pose_tools.landmark.model_manager."""

from pathlib import Path

import pytest

from pose_tools.landmark.model_manager import ModelManager
from pose_tools.landmark.model_manager import ModelNotFoundError


class TestModelManager:
    """Model path resolution."""

    def test_custom_model_dir(self, tmp_path: Path) -> None:
        mgr = ModelManager(model_dir=tmp_path)
        assert mgr.model_dir == tmp_path

    def test_get_model_path_no_exist_raises(self, tmp_path: Path) -> None:
        mgr = ModelManager(model_dir=tmp_path)
        with pytest.raises(ModelNotFoundError):
            mgr.get_model_path("pose_landmarker", must_exist=True)

    def test_get_model_path_must_exist_false(self, tmp_path: Path) -> None:
        mgr = ModelManager(model_dir=tmp_path)
        path = mgr.get_model_path("pose_landmarker", must_exist=False)
        assert path.name == "pose_landmarker.task"
        assert path.parent == tmp_path

    def test_get_model_path_exists(self, tmp_path: Path) -> None:
        model_file = tmp_path / "hand_landmarker.task"
        model_file.touch()
        mgr = ModelManager(model_dir=tmp_path)
        path = mgr.get_model_path("hand_landmarker", must_exist=True)
        assert path == model_file
