# Bazel Quick Start Guide

## Installation

```bash
# macOS
brew install bazel

# Or download from: https://github.com/bazelbuild/bazel/releases
```

## First Time Setup

1. **Generate requirements lock file** (if not already done):
   ```bash
   pip-compile requirements.txt -o requirements-lock.txt
   ```
   Or manually pin versions in `requirements-lock.txt`

2. **Initialize Bazel workspace**:
   ```bash
   bazel sync
   ```

## Basic Commands

### Build

```bash
# Build all services
bazel build //services/...

# Build specific service
bazel build //services/taskprocessing:taskprocessing

# Build Docker image
bazel build //services/taskprocessing:taskprocessing_docker
```

### Run

```bash
# Run a service locally
bazel run //services/taskprocessing:taskprocessing
```

### Test

```bash
# Run all tests
bazel test //...

# Run specific service tests
bazel test //services/taskprocessing/...
```

### Docker Images

```bash
# Build and load Docker image
bazel run //services/taskprocessing:taskprocessing_docker -- --norun
docker load -i bazel-bin/services/taskprocessing/taskprocessing_docker.tar
```

## Integration with Docker Compose

After building images with Bazel, load them and update `docker-compose.yml` to use the loaded images, or integrate Bazel build into your docker-compose workflow.

See `BAZEL_SETUP.md` for detailed documentation.

