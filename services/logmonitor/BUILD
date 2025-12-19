# BUILD file for Log Monitor Service

load("@rules_python//python:defs.bzl", "py_binary", "py_library")
# Docker rules disabled for now - will re-enable once WORKSPACE is fully configured
# load("@io_bazel_rules_docker//python3:image.bzl", "py3_image")

package(default_visibility = ["//visibility:public"])

# Log Monitor Service Library
py_library(
    name = "logmonitor_lib",
    srcs = glob(["app/**/*.py"], exclude = ["**/__pycache__/**", "**/test_*.py"]),
    data = glob(["app/**/*.html"]),
    deps = [
        "//common:pyportal_common",
        # Dependencies will be handled via system Python for now
        # TODO: Add pip_deps once pip_parse is configured
    ],
    imports = ["."],
)

# Log Monitor Service Binary (entry point)
py_binary(
    name = "logmonitor",
    srcs = ["wsgi.py"],
    main = "wsgi.py",
    deps = [":logmonitor_lib"],
)

# Docker image for Log Monitor Service
# Note: Disabled until Docker rules are configured in WORKSPACE
# py3_image(
#     name = "logmonitor_docker",
#     main = "wsgi.py",
#     srcs = ["wsgi.py"] + glob(["config/gunicorn_config.py"]),
#     deps = [":logmonitor_lib"],
# )

