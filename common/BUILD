# BUILD file for Common Library

package(default_visibility = ["//visibility:public"])

load("@rules_python//python:defs.bzl", "py_library")

# Common library (shared across all services)
py_library(
    name = "pyportal_common",
    srcs = glob(["pyportal_common/**/*.py"], exclude = ["**/__pycache__/**", "**/test_*.py"]),
    deps = [
        # Dependencies will be handled via system Python for now
        # TODO: Add pip_deps once pip_parse is configured
    ],
    imports = ["."],
)

