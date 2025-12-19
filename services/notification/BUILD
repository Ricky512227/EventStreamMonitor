# BUILD file for Notification Service

load("@rules_python//python:defs.bzl", "py_binary", "py_library")
# Docker rules disabled for now - will re-enable once WORKSPACE is fully configured
# load("@io_bazel_rules_docker//python3:image.bzl", "py3_image")

package(default_visibility = ["//visibility:public"])

# Notification Service Library
py_library(
    name = "notification_lib",
    srcs = glob(["app/**/*.py"], exclude = ["**/__pycache__/**", "**/test_*.py"]),
    deps = [
        "//common:pyportal_common",
        # Dependencies will be handled via system Python for now
        # TODO: Add pip_deps once pip_parse is configured
    ],
    imports = ["."],
)

# Notification Service Binary (entry point)
py_binary(
    name = "notification",
    srcs = ["wsgi.py"],
    main = "wsgi.py",
    deps = [":notification_lib"],
)

# Docker image for Notification Service
# Note: Disabled until Docker rules are configured in WORKSPACE
# py3_image(
#     name = "notification_docker",
#     main = "wsgi.py",
#     srcs = ["wsgi.py"] + glob(["gunicorn_config.py"]),
#     deps = [":notification_lib"],
# )

