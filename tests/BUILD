# BUILD file for Tests

package(default_visibility = ["//visibility:public"])

load("@rules_python//python:defs.bzl", "py_test", "py_library")

# Integration tests library
py_library(
    name = "integration_tests_lib",
    srcs = glob(["integration/**/*.py"], exclude = ["**/__pycache__/**", "**/jmeter_tests/**"]),
    deps = [
        "//common:pyportal_common",
        # Dependencies will be handled via system Python for now
        # TODO: Add pip_deps once pip_parse is configured
    ],
    imports = ["."],
)

# Integration tests
py_test(
    name = "integration_tests",
    srcs = glob(["integration/test_*.py"]),
    deps = [":integration_tests_lib"],
    # Note: Tests may require services to be running
)

# Unit tests library
py_library(
    name = "unit_tests_lib",
    srcs = glob(["pyportal_unit_tests/**/*.py"], exclude = ["**/__pycache__/**"]),
    deps = [
        "//common:pyportal_common",
    ],
    imports = ["."],
)

