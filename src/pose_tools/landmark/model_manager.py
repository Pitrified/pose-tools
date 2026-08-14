"""MediaPipe model manager.

Provides config-based model path resolution and validation for MediaPipe
``.task`` model files, and fetches them from Google's model CDN on request.
"""

from pathlib import Path
from typing import Literal
import urllib.request

from loguru import logger as lg

ModelType = Literal["pose_landmarker", "hand_landmarker", "face_landmarker"]

DEFAULT_MODEL_DIR = Path.home() / ".mediapipe" / "models"

MODEL_FILENAMES: dict[ModelType, str] = {
    "pose_landmarker": "pose_landmarker.task",
    "hand_landmarker": "hand_landmarker.task",
    "face_landmarker": "face_landmarker.task",
}

MODEL_CDN = "https://storage.googleapis.com/mediapipe-models"


def _model_url(family: ModelType, asset: str) -> str:
    """Build a CDN download URL.

    Args:
        family: Model family directory, which matches the model type.
        asset: Asset name, repeated in the path and in the filename.

    Returns:
        Full https URL to the ``.task`` file.
    """
    return f"{MODEL_CDN}/{family}/{asset}/float16/latest/{asset}.task"


# Download URLs per model type and variant. Only pose ships several variants,
# and only float16 weights are published, so precision is not a dimension here.
MODEL_URLS: dict[ModelType, dict[str, str]] = {
    "pose_landmarker": {
        "lite": _model_url("pose_landmarker", "pose_landmarker_lite"),
        "full": _model_url("pose_landmarker", "pose_landmarker_full"),
        "heavy": _model_url("pose_landmarker", "pose_landmarker_heavy"),
    },
    "hand_landmarker": {
        "default": _model_url("hand_landmarker", "hand_landmarker"),
    },
    "face_landmarker": {
        "default": _model_url("face_landmarker", "face_landmarker"),
    },
}

DEFAULT_VARIANTS: dict[ModelType, str] = {
    "pose_landmarker": "full",
    "hand_landmarker": "default",
    "face_landmarker": "default",
}

DOWNLOAD_TIMEOUT_S = 60.0


class ModelNotFoundError(FileNotFoundError):
    """Raised when a required MediaPipe model file is not found."""


class UnknownModelVariantError(ValueError):
    """Raised when a model variant is not one this library knows how to fetch."""

    def __init__(self, model_type: ModelType, variant: str) -> None:
        """Initialise with the offending variant and the ones that would work.

        Args:
            model_type: Model whose variants were consulted.
            variant: The variant that was asked for.
        """
        known = ", ".join(sorted(MODEL_URLS[model_type]))
        super().__init__(
            f"Unknown {model_type} variant {variant!r}, expected one of: {known}"
        )


class ModelDownloadError(RuntimeError):
    """Raised when fetching a model file from the CDN fails."""

    def __init__(self, url: str, reason: str) -> None:
        """Initialise with the URL that failed and why.

        Args:
            url: The URL that was being fetched.
            reason: Underlying failure, as text.
        """
        super().__init__(f"Failed to download {url}: {reason}")


class ModelManager:
    """Resolve and validate paths to MediaPipe model files.

    Args:
        model_dir: Base directory for model files.
            Defaults to ``~/.mediapipe/models``.
    """

    def __init__(self, model_dir: Path | None = None) -> None:
        """Initialize the model manager.

        Args:
            model_dir: Base directory for model files.
                Defaults to ``~/.mediapipe/models``.
        """
        self.model_dir = model_dir or DEFAULT_MODEL_DIR

    def get_model_path(
        self,
        model_type: ModelType,
        *,
        must_exist: bool = True,
    ) -> Path:
        """Return the path for a given model type.

        Args:
            model_type: Which model to locate.
            must_exist: If ``True`` (default) raise ``ModelNotFoundError``
                when the file is missing.

        Returns:
            Resolved model file path.
        """
        filename = MODEL_FILENAMES[model_type]
        path = self.model_dir / filename

        if must_exist and not path.exists():
            msg = (
                f"Model file not found: {path}\n"
                f"Download it from https://developers.google.com/mediapipe/solutions/vision"
                f" and place it in {self.model_dir}"
            )
            raise ModelNotFoundError(msg)

        lg.debug(f"Resolved {model_type} model: {path}")
        return path

    def ensure_model(
        self,
        model_type: ModelType,
        variant: str | None = None,
        *,
        force: bool = False,
        timeout: float = DOWNLOAD_TIMEOUT_S,
    ) -> Path:
        """Return the path to a model file, downloading it if it is missing.

        This is the only method that touches the network, and it only does so
        when the file is absent or *force* is set. ``get_model_path()`` never
        downloads.

        The file is written to a temporary ``.part`` neighbour and renamed once
        the download completes, so an interrupted fetch leaves no file rather
        than a truncated one.

        Args:
            model_type: Which model to fetch.
            variant: Which variant to fetch. Defaults to the entry in
                ``DEFAULT_VARIANTS`` (``full`` for pose, the only variant for
                the others).
            force: Download again even if the file is already present.
            timeout: Socket timeout in seconds for the download.

        Returns:
            Path to the model file, which exists on return.

        Raises:
            UnknownModelVariantError: If *variant* is not a known variant.
            ModelDownloadError: If the download or the write fails.
        """
        chosen = variant or DEFAULT_VARIANTS[model_type]
        if chosen not in MODEL_URLS[model_type]:
            raise UnknownModelVariantError(model_type, chosen)

        path = self.get_model_path(model_type, must_exist=False)
        if path.exists() and not force:
            lg.debug(f"{model_type} already present: {path}")
            return path

        url = MODEL_URLS[model_type][chosen]
        lg.info(f"Downloading {model_type} ({chosen}) from {url}")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        partial = path.with_name(f"{path.name}.part")

        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:  # noqa: S310 - URL comes from MODEL_URLS, https only
                partial.write_bytes(response.read())
        # URLError and HTTPError are both OSError subclasses, as are write failures.
        except OSError as exc:
            partial.unlink(missing_ok=True)
            raise ModelDownloadError(url, str(exc)) from exc

        partial.replace(path)
        lg.info(f"Saved {model_type} to {path}")
        return path
