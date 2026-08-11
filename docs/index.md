# Pose Tools

Welcome to the **Pose Tools** documentation.

Pose Tools is an installable Python library for pose tracking and analysis. It provides common utilities for working with pose data, including MediaPipe integration (hand and pose landmarkers), video frame loading, OpenCV/matplotlib display helpers, numpy-based landmark arrays with visibility masking, homography utilities, and landmark distance computation.

It exists to hold code shared across the pose projects. `abyss` consumes it today, pinned by git tag; `climbing-wire` and `holo-table` still carry their own copies and are the intended next consumers.

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
make sync

# Lint, typecheck and test
make check

# Start documentation server
make docs
```

## Project Structure

```
pose-tools/
├── src/pose_tools/       # Main library code
│   ├── geometry/           # Homography and signal tracking
│   ├── landmark/           # MediaPipe landmarkers, arrays, drawing
│   ├── metaclasses/        # Singleton metaclass
│   ├── params/             # Paths
│   ├── utils/              # MediaPipe, OpenCV, matplotlib, numpy helpers
│   └── video/              # Frames and video iteration
├── tests/                  # Test suite
├── docs/                   # Documentation (you are here)
└── scratch_space/          # Experimental notebooks
```

## Next Steps

- [Getting Started](getting-started.md) - Set up your development environment
- [Guides](guides/uv.md) - Learn about the tools used in this project
- [API Reference](reference/) - Explore the codebase
