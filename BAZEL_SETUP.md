# Bazel Build System Setup for EventStreamMonitor

This document explains how to use Bazel to build, test, and deploy the EventStreamMonitor microservices.

## What Bazel Provides

Bazel offers several advantages over traditional Docker-based builds:

### 1. **Fast, Incremental Builds**
- Only rebuilds what changed
- Parallel execution of independent tasks
- Smart caching reduces build times significantly

### 2. **Reproducible Builds**
- Same inputs always produce same outputs
- Deterministic builds across different environments
- Eliminates "works on my machine" issues

### 3. **Dependency Management**
- Explicit dependency graph
- Automatic dependency resolution
- Prevents circular dependencies

### 4. **Multi-Language Support**
- Builds Python code, proto files, and Docker images
- Consistent build process across all components

### 5. **Testing**
- Run tests with proper isolation
- Parallel test execution
- Better test reporting

### 6. **Remote Caching** (Optional)
- Share build cache across team
- Faster CI/CD pipelines
- Reduced build times in cloud environments

## Prerequisites

1. **Install Bazel**: Follow instructions at https://bazel.build/install
   ```bash
   # macOS
   brew install bazel
   
   # Or download from: https://github.com/bazelbuild/bazel/releases
   ```

2. **Verify Installation**:
   ```bash
   bazel version
   ```

## Project Structure

```
EventStreamMonitor/
├── WORKSPACE              # Bazel workspace configuration
├── BUILD                  # Root BUILD file
├── .bazelrc              # Bazel configuration flags
├── requirements-lock.txt  # Pinned Python dependencies
├── common/               # Shared library
│   └── BUILD            # (to be created)
├── proto/               # Protocol buffer definitions
│   └── BUILD           # (included in root BUILD)
└── services/           # Microservices
    ├── taskprocessing/
    │   └── BUILD       # Service BUILD file
    ├── usermanagement/
    │   └── BUILD
    ├── notification/
    │   └── BUILD
    └── logmonitor/
        └── BUILD
```

## Basic Bazel Commands

### Build All Services

```bash
# Build all services
bazel build //services/...

# Build specific service
bazel build //services/taskprocessing:taskprocessing

# Build Docker image
bazel build //services/taskprocessing:taskprocessing_docker
```

### Run Services Locally

```bash
# Run a service
bazel run //services/taskprocessing:taskprocessing

# Run with custom arguments
bazel run //services/taskprocessing:taskprocessing -- --port=9092
```

### Test Services

```bash
# Run all tests
bazel test //...

# Run tests for specific service
bazel test //services/taskprocessing/...

# Run tests with output
bazel test //services/taskprocessing/... --test_output=all
```

### Build Docker Images

```bash
# Build Docker image for a service
bazel build //services/taskprocessing:taskprocessing_docker

# Load image into local Docker (after building)
docker load -i bazel-bin/services/taskprocessing/taskprocessing_docker.tar

# Or use bazel run to build and load
bazel run //services/taskprocessing:taskprocessing_docker -- --norun
```

### Query Build Graph

```bash
# See dependencies of a target
bazel query --output=graph //services/taskprocessing:taskprocessing | dot -Tpng > deps.png

# List all targets
bazel query //...

# Find what depends on common library
bazel query 'rdeps(//..., //:common)'
```

## Integration with Docker Compose

You can use Bazel-built images with Docker Compose:

1. **Build images with Bazel**:
   ```bash
   bazel build //services/...
   bazel build //services/taskprocessing:taskprocessing_docker
   bazel build //services/usermanagement:usermanagement_docker
   bazel build //services/notification:notification_docker
   bazel build //services/logmonitor:logmonitor_docker
   ```

2. **Load images into Docker**:
   ```bash
   docker load -i bazel-bin/services/taskprocessing/taskprocessing_docker.tar
   docker load -i bazel-bin/services/usermanagement/usermanagement_docker.tar
   docker load -i bazel-bin/services/notification/notification_docker.tar
   docker load -i bazel-bin/services/logmonitor/logmonitor_docker.tar
   ```

3. **Tag images** (optional):
   ```bash
   docker tag bazel/services/taskprocessing:taskprocessing_docker eventstreammonitor-taskprocessing-service:latest
   ```

4. **Use in docker-compose.yml** (update image references)

## Common Use Cases

### Development Workflow

1. **Make code changes**
2. **Build only what changed**:
   ```bash
   bazel build //services/taskprocessing:taskprocessing
   ```
3. **Run service locally**:
   ```bash
   bazel run //services/taskprocessing:taskprocessing
   ```

### CI/CD Pipeline

```bash
# Build all services
bazel build //services/...

# Run all tests
bazel test //...

# Build Docker images
bazel build //services/...:..._docker

# Push images (after loading)
docker push your-registry/eventstreammonitor-taskprocessing-service:latest
```

### Debugging Builds

```bash
# Verbose output
bazel build //services/taskprocessing:taskprocessing --verbose_failures

# See what commands would run (dry run)
bazel build //services/taskprocessing:taskprocessing --nobuild

# Clean build (remove cache)
bazel clean
bazel build //services/taskprocessing:taskprocessing
```

## Advanced Features

### Remote Caching

Configure remote cache in `.bazelrc`:

```bazelrc
build --remote_cache=https://your-cache-server.com
```

### Build Performance

```bash
# Use more jobs (parallel builds)
bazel build //... --jobs=16

# Profile build
bazel build //... --profile=profile.json
# View: chrome://tracing -> load profile.json
```

### Python Dependencies

Update `requirements-lock.txt` with pinned versions, then:

```bash
# Update pip dependencies
bazel sync --only=pip_deps

# Or manually update in WORKSPACE
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors**:
   - Check `deps` in BUILD files
   - Ensure imports match package structure
   - Run `bazel clean --expunge` and rebuild

2. **Proto compilation errors**:
   - Verify proto file paths in BUILD
   - Check proto syntax and imports

3. **Docker image build fails**:
   - Ensure base image is available
   - Check file paths in `container_image` rule

4. **Slow builds**:
   - Use remote caching
   - Increase `--jobs` flag
   - Check for unnecessary dependencies

## Next Steps

1. **Fine-tune BUILD files** for each service's specific needs
2. **Add test targets** using `py_test` rules
3. **Set up remote caching** for team/CI
4. **Integrate with CI/CD** (GitHub Actions, Jenkins, etc.)
5. **Create deployment scripts** using Bazel-built images

## Resources

- [Bazel Documentation](https://bazel.build/docs)
- [Rules Python](https://github.com/bazelbuild/rules_python)
- [Rules Docker](https://github.com/bazelbuild/rules_docker)
- [Rules Proto](https://github.com/bazelbuild/rules_proto)

