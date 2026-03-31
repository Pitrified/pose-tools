# Pose Tools

Welcome to the **Pose Tools** documentation.

Pose Tools is an installable Python library for pose tracking and analysis. It provides common utilities for working with pose data, including MediaPipe integration (hand and pose landmarkers), video frame loading, OpenCV/matplotlib display helpers, numpy-based landmark arrays with visibility masking, homography utilities, and landmark distance computation.

It extracts and unifies shared code from three pose-related projects: `climbing-wire`, `holo-table`, and `abyss`.

## Features

- **Video frame handling**: Unified `Frame` dataclass wrapping MediaPipe images, with factory methods and video iteration
- **MediaPipe integration**: Wrappers for pose and hand landmarkers using the Tasks API
- **Landmark arrays**: Numpy-based landmark representations with visibility masking and pixel coordinate conversion
- **Display helpers**: OpenCV and matplotlib utilities for visualizing frames and landmarks
- **Geometry utilities**: Homography computation, coordinate conversion, landmark distance measurement

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Pitrified/pose-tools.git
cd pose-tools

# Install dependencies
uv sync --all-extras --all-groups

# Run tests
uv run pytest

# Start documentation server
uv run mkdocs serve
```

## Project Structure

```
pose-tools/
├── src/pose_tools/       # Main library code
│   ├── config/             # Configuration models
│   ├── data_models/        # Pydantic base models
│   ├── metaclasses/        # Singleton metaclass
│   └── params/             # Parameters and paths
├── tests/                  # Test suite
├── docs/                   # Documentation (you are here)
└── scratch_space/          # Experimental notebooks
```

## Next Steps

- [Getting Started](getting-started.md) - Set up your development environment
- [Guides](guides/uv.md) - Learn about the tools used in this project
- [API Reference](reference/) - Explore the codebase
