# Bazel BUILD Files Structure

## Overview

All BUILD files have been created for the EventStreamMonitor project. Here's the complete structure:

## BUILD Files Created

1. **Root BUILD** (`./BUILD`)
   - Provides alias for common library for backwards compatibility
   - References `//common:pyportal_common`

2. **Common Library** (`./common/BUILD`)
   - Defines `pyportal_common` library
   - Contains shared code used across all services

3. **Services** (each service has its own BUILD file):
   - `./services/usermanagement/BUILD` - User Management Service
   - `./services/taskprocessing/BUILD` - Task Processing Service
   - `./services/notification/BUILD` - Notification Service
   - `./services/logmonitor/BUILD` - Log Monitor Service
   - `./services/auth/BUILD` - Auth Service (gRPC-based)

4. **Protocol Buffers** (`./proto/BUILD`)
   - For proto file compilation (currently disabled until rules_proto is configured)

5. **Tests** (`./tests/BUILD`)
   - Integration tests
   - Unit tests

## BUILD File Structure

### Common Pattern for Services

Each service BUILD file follows this pattern:

```python
# Service Library
py_library(
    name = "{service}_lib",
    srcs = glob(["app/**/*.py"], exclude = ["**/__pycache__/**", "**/test_*.py"]),
    deps = ["//common:pyportal_common"],
)

# Service Binary
py_binary(
    name = "{service}",
    srcs = ["wsgi.py"],
    main = "wsgi.py",
    deps = [":{service}_lib"],
)
```

### Dependencies

All services depend on:
- `//common:pyportal_common` - The shared common library

Future additions (once pip_parse is configured):
- Python package dependencies via `@pip_deps//...`

## Usage

### Build a Service

```bash
# Build specific service
bazel build //services/taskprocessing:taskprocessing

# Build all services
bazel build //services/...

# Build common library
bazel build //common:pyportal_common
```

### Run a Service

```bash
bazel run //services/taskprocessing:taskprocessing
```

### Build Tests

```bash
bazel build //tests:integration_tests
bazel test //tests:integration_tests
```

## Current Status

- ✅ All BUILD files created
- ✅ Dependencies properly defined
- ⚠️ Python package dependencies need to be configured (pip_parse)
- ⚠️ Docker image building disabled (waiting for rules_docker configuration)
- ⚠️ Proto compilation disabled (waiting for rules_proto configuration)

