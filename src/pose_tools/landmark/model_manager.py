"""MediaPipe model manager.

Provides config-based model path resolution and validation for MediaPipe
``.task`` model files.
"""

from pathlib import Path
from typing import Literal

from loguru import logger as lg

ModelType = Literal["pose_landmarker", "hand_landmarker"]

DEFAULT_MODEL_DIR = Path.home() / ".mediapipe" / "models"

MODEL_FILENAMES: dict[ModelType, str] = {
    "pose_landmarker": "pose_landmarker.task",
    "hand_landmarker": "hand_landmarker.task",
}


class ModelNotFoundError(FileNotFoundError):
    """Raised when a required MediaPipe model file is not found."""


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
