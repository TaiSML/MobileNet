load("//tensorflow:strict.default.bzl", "py_strict_library", "py_strict_test")

package(
    # copybara:uncomment default_applicable_licenses = ["//tensorflow:license"],
    default_visibility = ["//tensorflow:internal"],
    licenses = ["notice"],
)

py_strict_library(
    name = "nest",
    srcs = ["nest.py"],
    srcs_version = "PY3",
    deps = [
        "//tensorflow/python/util:nest_util",
    ],
)

py_strict_test(
    name = "nest_test",
    size = "small",
    srcs = ["nest_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":nest",
        "//tensorflow/python:array_ops",
        "//tensorflow/python:client_testlib",
        "//tensorflow/python:math_ops",
        "//tensorflow/python/data/kernel_tests:test_base",
        "//tensorflow/python/framework:combinations",
        "//tensorflow/python/framework:constant_op",
        "//tensorflow/python/framework:sparse_tensor",
        "//tensorflow/python/ops/ragged:ragged_factory_ops",
        "//third_party/py/numpy",
        "@absl_py//absl/testing:parameterized",
    ],
)

py_strict_library(
    name = "sparse",
    srcs = ["sparse.py"],
    srcs_version = "PY3",
    deps = [
        ":nest",
        "//tensorflow/python:dtypes",
        "//tensorflow/python:sparse_ops",
        "//tensorflow/python:sparse_tensor",
        "//tensorflow/python:tensor_shape",
        "//tensorflow/python/framework:ops",
    ],
)

py_strict_test(
    name = "sparse_test",
    size = "small",
    srcs = ["sparse_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":nest",
        ":sparse",
        "//tensorflow/python:client_testlib",
        "//tensorflow/python:dtypes",
        "//tensorflow/python:sparse_tensor",
        "//tensorflow/python:tensor_shape",
        "//tensorflow/python/data/kernel_tests:test_base",
        "//tensorflow/python/framework:combinations",
        "//tensorflow/python/framework:constant_op",
        "//tensorflow/python/framework:ops",
        "@absl_py//absl/testing:parameterized",
    ],
)

py_strict_library(
    name = "structure",
    srcs = ["structure.py"],
    srcs_version = "PY3",
    deps = [
        ":nest",
        "//tensorflow/python:framework_ops",
        "//tensorflow/python:resource_variable_ops",
        "//tensorflow/python:sparse_tensor",
        "//tensorflow/python:tensor_array_ops",
        "//tensorflow/python:tensor_shape",
        "//tensorflow/python/framework:composite_tensor",
        "//tensorflow/python/framework:tensor_spec",
        "//tensorflow/python/framework:type_spec",
        "//tensorflow/python/framework:type_spec_registry",
        "//tensorflow/python/ops/ragged:ragged_tensor",
        "//tensorflow/python/platform:tf_logging",
        "//tensorflow/python/types:internal",
        "//tensorflow/python/util:compat",
        "//tensorflow/python/util:deprecation",
        "//tensorflow/python/util:tf_export",
        "@wrapt",
    ],
)

py_strict_test(
    name = "structure_test",
    size = "small",
    srcs = ["structure_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":nest",
        ":structure",
        "//tensorflow/python:array_ops",
        "//tensorflow/python:client_testlib",
        "//tensorflow/python:constant_op",
        "//tensorflow/python:dtypes",
        "//tensorflow/python:framework_ops",
        "//tensorflow/python:sparse_tensor",
        "//tensorflow/python:tensor_array_ops",
        "//tensorflow/python:tensor_shape",
        "//tensorflow/python:tensor_spec",
        "//tensorflow/python:variables",
        "//tensorflow/python/data/kernel_tests:test_base",
        "//tensorflow/python/data/ops:dataset_ops",
        "//tensorflow/python/framework:combinations",
        "//tensorflow/python/ops/ragged:ragged_factory_ops",
        "//tensorflow/python/ops/ragged:ragged_tensor",
        "//tensorflow/python/ops/ragged:ragged_tensor_value",
        "//tensorflow/python/util:compat",
        "//third_party/py/numpy",
        "@absl_py//absl/testing:parameterized",
        "@wrapt",
    ],
)

py_strict_library(
    name = "options",
    srcs = ["options.py"],
    srcs_version = "PY3",
    deps = ["@absl_py//absl/logging"],
)

py_strict_test(
    name = "options_test",
    size = "small",
    srcs = ["options_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":options",
        "//tensorflow/python:client_testlib",
        "//tensorflow/python/data/kernel_tests:test_base",
        "//tensorflow/python/framework:combinations",
        "@absl_py//absl/testing:parameterized",
    ],
)

py_strict_library(
    name = "convert",
    srcs = ["convert.py"],
    srcs_version = "PY3",
    deps = [
        "//tensorflow/python:constant_op",
        "//tensorflow/python:dtypes",
        "//tensorflow/python:framework_ops",
        "//tensorflow/python:tensor_shape",
    ],
)

py_strict_test(
    name = "convert_test",
    size = "small",
    srcs = ["convert_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":convert",
        "//tensorflow/python:client_testlib",
        "//tensorflow/python:framework_for_generated_wrappers",
        "//tensorflow/python/data/kernel_tests:test_base",
        "//tensorflow/python/framework:combinations",
        "//tensorflow/python/framework:constant_op",
        "//tensorflow/python/util:compat",
        "@absl_py//absl/testing:parameterized",
    ],
)

py_strict_library(
    name = "random_seed",
    srcs = ["random_seed.py"],
    srcs_version = "PY3",
    deps = [
        "//tensorflow/python:array_ops",
        "//tensorflow/python:constant_op",
        "//tensorflow/python:dtypes",
        "//tensorflow/python:math_ops",
        "//tensorflow/python/framework:ops",
        "//tensorflow/python/framework:random_seed",
    ],
)

py_strict_test(
    name = "random_seed_test",
    size = "medium",
    srcs = ["random_seed_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":random_seed",
        "//tensorflow/python:client_testlib",
        "//tensorflow/python:framework_for_generated_wrappers",
        "//tensorflow/python/data/kernel_tests:test_base",
        "//tensorflow/python/framework:combinations",
        "//tensorflow/python/framework:constant_op",
        "//tensorflow/python/framework:random_seed",
        "@absl_py//absl/testing:parameterized",
    ],
)

py_strict_library(
    name = "traverse",
    srcs = ["traverse.py"],
    srcs_version = "PY3",
    deps = [
        "//tensorflow/python/framework:dtypes",
    ],
)

py_strict_test(
    name = "traverse_test",
    size = "small",
    srcs = ["traverse_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":traverse",
        "//tensorflow/python:client_testlib",
        "//tensorflow/python:math_ops",
        "//tensorflow/python/compat",
        "//tensorflow/python/data/experimental/ops:dataset_ops",
        "//tensorflow/python/data/kernel_tests:test_base",
        "//tensorflow/python/data/ops:dataset_ops",
        "//tensorflow/python/framework:combinations",
        "@absl_py//absl/testing:parameterized",
    ],
)
