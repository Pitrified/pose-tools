"""Tests for pose_tools.landmark.model_manager."""

from collections.abc import Iterator
import contextlib
from pathlib import Path
from typing import get_args
import urllib.error

import pytest

from pose_tools.landmark import model_manager
from pose_tools.landmark.model_manager import DEFAULT_VARIANTS
from pose_tools.landmark.model_manager import MODEL_FILENAMES
from pose_tools.landmark.model_manager import MODEL_URLS
from pose_tools.landmark.model_manager import ModelDownloadError
from pose_tools.landmark.model_manager import ModelManager
from pose_tools.landmark.model_manager import ModelNotFoundError
from pose_tools.landmark.model_manager import ModelType
from pose_tools.landmark.model_manager import UnknownModelVariantError


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


class TestRegistry:
    """The download tables cover what the library claims to know."""

    def test_every_model_type_has_a_filename(self) -> None:
        assert set(MODEL_FILENAMES) == set(get_args(ModelType))

    def test_every_model_type_has_urls(self) -> None:
        assert set(MODEL_URLS) == set(get_args(ModelType))

    def test_every_default_variant_exists(self) -> None:
        for model_type, variant in DEFAULT_VARIANTS.items():
            assert variant in MODEL_URLS[model_type]

    def test_urls_are_https_task_files(self) -> None:
        for variants in MODEL_URLS.values():
            for url in variants.values():
                assert url.startswith("https://")
                assert url.endswith(".task")


def fake_opener(payload: bytes) -> object:
    """Build a stand-in for ``urlopen`` that yields *payload*.

    Args:
        payload: Bytes the fake response returns from ``read()``.

    Returns:
        A callable with ``urlopen``'s context-manager shape.
    """

    class FakeResponse:
        def read(self) -> bytes:
            return payload

    @contextlib.contextmanager
    def opener(url: str, timeout: float = 0.0) -> Iterator[FakeResponse]:
        yield FakeResponse()

    return opener


def failing_opener(exc: Exception) -> object:
    """Build a stand-in for ``urlopen`` that raises *exc* when called."""

    def opener(url: str, timeout: float = 0.0) -> object:
        raise exc

    return opener


def exploding_opener(url: str, timeout: float = 0.0) -> object:
    """Fail the test: this opener must never be called."""
    msg = "the network was used when the file was already present"
    raise AssertionError(msg)


class TestEnsureModel:
    """Fetching model files."""

    def test_returns_existing_file_without_downloading(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        model_file = tmp_path / "face_landmarker.task"
        model_file.write_bytes(b"already here")
        monkeypatch.setattr(model_manager.urllib.request, "urlopen", exploding_opener)

        mgr = ModelManager(model_dir=tmp_path)
        assert mgr.ensure_model("face_landmarker") == model_file
        assert model_file.read_bytes() == b"already here"

    def test_downloads_a_missing_model(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            model_manager.urllib.request, "urlopen", fake_opener(b"model bytes")
        )

        mgr = ModelManager(model_dir=tmp_path)
        path = mgr.ensure_model("face_landmarker")

        assert path == tmp_path / "face_landmarker.task"
        assert path.read_bytes() == b"model bytes"

    def test_creates_the_model_dir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            model_manager.urllib.request, "urlopen", fake_opener(b"model bytes")
        )

        mgr = ModelManager(model_dir=tmp_path / "nested" / "models")
        assert mgr.ensure_model("hand_landmarker").exists()

    def test_force_redownloads(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        model_file = tmp_path / "hand_landmarker.task"
        model_file.write_bytes(b"stale")
        monkeypatch.setattr(
            model_manager.urllib.request, "urlopen", fake_opener(b"fresh")
        )

        mgr = ModelManager(model_dir=tmp_path)
        assert mgr.ensure_model("hand_landmarker", force=True).read_bytes() == b"fresh"

    def test_unknown_variant_raises_before_the_network(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(model_manager.urllib.request, "urlopen", exploding_opener)

        mgr = ModelManager(model_dir=tmp_path)
        with pytest.raises(UnknownModelVariantError, match="Unknown pose_landmarker"):
            mgr.ensure_model("pose_landmarker", "enormous")

    def test_variant_selects_the_url(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        seen: list[str] = []

        @contextlib.contextmanager
        def recording_opener(url: str, timeout: float = 0.0) -> Iterator[object]:
            seen.append(url)

            class FakeResponse:
                def read(self) -> bytes:
                    return b"lite bytes"

            yield FakeResponse()

        monkeypatch.setattr(model_manager.urllib.request, "urlopen", recording_opener)

        ModelManager(model_dir=tmp_path).ensure_model("pose_landmarker", "lite")
        assert seen == [MODEL_URLS["pose_landmarker"]["lite"]]

    def test_failed_download_leaves_no_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            model_manager.urllib.request,
            "urlopen",
            failing_opener(urllib.error.URLError("no route to host")),
        )

        mgr = ModelManager(model_dir=tmp_path)
        with pytest.raises(ModelDownloadError):
            mgr.ensure_model("face_landmarker")

        assert list(tmp_path.iterdir()) == []
