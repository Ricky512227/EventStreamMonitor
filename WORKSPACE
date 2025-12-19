workspace(name = "eventstreammonitor")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Bazel version
BAZEL_VERSION = "7.0.0"

# Python rules (for Python dependencies and builds)
http_archive(
    name = "rules_python",
    sha256 = "9d04041ac92a0985e344235f5d946f71ac543f1b1565f2cdbc9a2aaee8adf55b",
    strip_prefix = "rules_python-0.26.0",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.26.0/rules_python-0.26.0.tar.gz",
)

load("@rules_python//python:repositories.bzl", "py_repositories", "python_register_toolchains")

py_repositories()

python_register_toolchains(
    name = "python3_9",
    python_version = "3.9",
)

# Docker rules (for building Docker images)
# Note: Temporarily disabled - will add back after basic build works
# http_archive(
#     name = "io_bazel_rules_docker",
#     sha256 = "b1e80761a8a8243d03ebca8845e9ccb162d8c7f75e8e26633c5848c4f5aa84a4",
#     strip_prefix = "rules_docker-0.27.0",
#     url = "https://github.com/bazelbuild/rules_docker/releases/download/v0.27.0/rules_docker-v0.27.0.tar.gz",
# )

# Proto rules (for gRPC and Protocol Buffers)
# Note: Temporarily disabled - will add back after basic build works
# http_archive(
#     name = "rules_proto",
#     sha256 = "dc3fb206a2cb3441b485eb1e423165b231235a1ea9b031b4433cf7bc1fa460dd",
#     strip_prefix = "rules_proto-5.3.0-21.7",
#     url = "https://github.com/bazelbuild/rules_proto/archive/refs/tags/5.3.0-21.7.tar.gz",
# )

# Python dependencies (pip packages)
# Note: Using a simpler approach for now - can use pip_parse later
# load("@rules_python//python:pip.bzl", "pip_parse")
# pip_parse(
#     name = "pip_deps",
#     requirements_lock = "//:requirements-lock.txt",
# )
# load("@pip_deps//:requirements.bzl", pip_requirements_install = "install_deps")
# pip_requirements_install()

