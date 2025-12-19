# BUILD file for Auth Service (gRPC service)

package(default_visibility = ["//visibility:public"])

load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# Auth Service Library (gRPC-based)
py_library(
    name = "auth_lib",
    srcs = glob(["app/**/*.py"], exclude = ["**/__pycache__/**", "**/test_*.py", "**/migrations/**"]),
    deps = [
        "//common:pyportal_common",
        # Dependencies will be handled via system Python for now
        # TODO: Add pip_deps once pip_parse is configured
    ],
    imports = ["."],
)

# Auth Service Binary (gRPC server entry point)
# Note: This service uses gRPC, not Flask/WSGI
py_binary(
    name = "auth",
    srcs = ["app/__init__.py"],
    main = "app/__init__.py",
    deps = [":auth_lib"],
)

