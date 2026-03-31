"""Test that the environment variables are available."""

import os


def test_env_vars() -> None:
    """The environment var POSE_TOOLS_SAMPLE_ENV_VAR is available."""
    assert "POSE_TOOLS_SAMPLE_ENV_VAR" in os.environ
    assert os.environ["POSE_TOOLS_SAMPLE_ENV_VAR"] == "sample"
