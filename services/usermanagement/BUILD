# BUILD file for User Management Service

load("@rules_python//python:defs.bzl", "py_binary", "py_library")
# Docker rules disabled for now - will re-enable once WORKSPACE is fully configured
# load("@io_bazel_rules_docker//python3:image.bzl", "py3_image")

package(default_visibility = ["//visibility:public"])

# User Management Service Library
py_library(
    name = "usermanagement_lib",
    srcs = glob(["app/**/*.py"], exclude = ["**/__pycache__/**", "**/test_*.py"]),
    deps = [
        "//common:pyportal_common",
        # Dependencies will be handled via system Python for now
        # TODO: Add pip_deps once pip_parse is configured
    ],
    imports = ["."],
)

# User Management Service Binary (entry point)
py_binary(
    name = "usermanagement",
    srcs = ["wsgi.py"],
    main = "wsgi.py",
    deps = [":usermanagement_lib"],
)

# Docker image for User Management Service
# Note: Disabled until Docker rules are configured in WORKSPACE
# py3_image(
#     name = "usermanagement_docker",
#     main = "wsgi.py",
#     srcs = ["wsgi.py"] + glob(["gunicorn_config.py"]),
#     deps = [":usermanagement_lib"],
# )

