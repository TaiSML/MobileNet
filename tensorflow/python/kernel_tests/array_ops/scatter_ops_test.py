# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for tensorflow.ops.tf.scatter."""

import numpy as np

from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import errors
from tensorflow.python.framework import test_util
from tensorflow.python.ops import ref_variable
from tensorflow.python.ops import state_ops
from tensorflow.python.ops import variables
from tensorflow.python.platform import test


def _AsType(v, vtype):
  return v.astype(vtype) if isinstance(v, np.ndarray) else vtype(v)


def _NumpyAdd(ref, indices, updates):
  # Since numpy advanced assignment does not support repeated indices,
  # we run a simple loop to perform scatter_add.
  for i, indx in np.ndenumerate(indices):
    ref[indx] += updates[i]


def _NumpyAddScalar(ref, indices, update):
  for _, indx in np.ndenumerate(indices):
    ref[indx] += update


def _NumpySub(ref, indices, updates):
  for i, indx in np.ndenumerate(indices):
    ref[indx] -= updates[i]


def _NumpySubScalar(ref, indices, update):
  for _, indx in np.ndenumerate(indices):
    ref[indx] -= update


def _NumpyMul(ref, indices, updates):
  for i, indx in np.ndenumerate(indices):
    ref[indx] *= updates[i]


def _NumpyMulScalar(ref, indices, update):
  for _, indx in np.ndenumerate(indices):
    ref[indx] *= update


def _NumpyDiv(ref, indices, updates):
  for i, indx in np.ndenumerate(indices):
    ref[indx] /= updates[i]


def _NumpyDivScalar(ref, indices, update):
  for _, indx in np.ndenumerate(indices):
    ref[indx] /= update


def _NumpyMin(ref, indices, updates):
  for i, indx in np.ndenumerate(indices):
    ref[indx] = np.minimum(ref[indx], updates[i])


def _NumpyMinScalar(ref, indices, update):
  for _, indx in np.ndenumerate(indices):
    ref[indx] = np.minimum(ref[indx], update)


def _NumpyMax(ref, indices, updates):
  for i, indx in np.ndenumerate(indices):
    ref[indx] = np.maximum(ref[indx], updates[i])


def _NumpyMaxScalar(ref, indices, update):
  for _, indx in np.ndenumerate(indices):
    ref[indx] = np.maximum(ref[indx], update)


def _NumpyUpdate(ref, indices, updates):
  for i, indx in np.ndenumerate(indices):
    ref[indx] = updates[i]


def _NumpyUpdateScalar(ref, indices, update):
  for _, indx in np.ndenumerate(indices):
    ref[indx] = update


_TF_OPS_TO_NUMPY = {
    state_ops.scatter_update: _NumpyUpdate,
    state_ops.scatter_add: _NumpyAdd,
    state_ops.scatter_sub: _NumpySub,
    state_ops.scatter_mul: _NumpyMul,
    state_ops.scatter_div: _NumpyDiv,
    state_ops.scatter_min: _NumpyMin,
    state_ops.scatter_max: _NumpyMax,
}

_TF_OPS_TO_NUMPY_SCALAR = {
    state_ops.scatter_update: _NumpyUpdateScalar,
    state_ops.scatter_add: _NumpyAddScalar,
    state_ops.scatter_sub: _NumpySubScalar,
    state_ops.scatter_mul: _NumpyMulScalar,
    state_ops.scatter_div: _NumpyDivScalar,
    state_ops.scatter_min: _NumpyMinScalar,
    state_ops.scatter_max: _NumpyMaxScalar,
}


class ScatterTest(test.TestCase):

  def _VariableRankTest(self,
                        tf_scatter,
                        vtype,
                        itype,
                        repeat_indices=False,
                        updates_are_scalar=False):
    np.random.seed(8)
    with self.cached_session():
      for indices_shape in (), (2,), (3, 7), (3, 4, 7):
        for extra_shape in (), (5,), (5, 9):
          # Generate random indices with no duplicates for easy numpy comparison
          size = np.prod(indices_shape, dtype=itype)
          first_dim = 3 * size
          indices = np.arange(first_dim)
          np.random.shuffle(indices)
          indices = indices[:size]
          if size > 1 and repeat_indices:
            # Add some random repeats.
            indices = indices[:size // 2]
            for _ in range(size - size // 2):
              # Randomly append some repeats.
              indices = np.append(indices,
                                  indices[np.random.randint(size // 2)])
            np.random.shuffle(indices)
          indices = indices.reshape(indices_shape)
          if updates_are_scalar:
            updates = _AsType(np.random.randn(), vtype)
          else:
            updates = _AsType(
                np.random.randn(*(indices_shape + extra_shape)), vtype)

          # Clips small values to avoid division by zero.
          threshold = np.array(1e-4, dtype=vtype)
          sign = np.sign(updates)
          if vtype == np.int32:
            threshold = 1
            sign = np.random.choice([-1, 1], updates.shape)
          updates = np.where(
              np.abs(updates) < threshold, threshold * sign, updates)

          old = _AsType(np.random.randn(*((first_dim,) + extra_shape)), vtype)

          # Scatter via numpy
          new = old.copy()
          if updates_are_scalar:
            np_scatter = _TF_OPS_TO_NUMPY_SCALAR[tf_scatter]
          else:
            np_scatter = _TF_OPS_TO_NUMPY[tf_scatter]
          np_scatter(new, indices, updates)
          # Scatter via tensorflow
          ref = variables.Variable(old)
          self.evaluate(ref.initializer)
          self.evaluate(tf_scatter(ref, indices, updates))
          self.assertAllCloseAccordingToType(
              self.evaluate(ref),
              new,
              half_rtol=5e-3,
              half_atol=5e-3,
              bfloat16_rtol=5e-2,
              bfloat16_atol=5e-2)

  def _VariableRankTests(self,
                         tf_scatter,
                         repeat_indices=False,
                         updates_are_scalar=False):
    vtypes = [np.float32, np.float64, dtypes.bfloat16.as_numpy_dtype]
    if tf_scatter != state_ops.scatter_div:
      vtypes.append(np.int32)
      # float16 is numerically unstable for div
      vtypes.append(np.float16)

    for vtype in vtypes:
      for itype in (np.int32, np.int64):
        self._VariableRankTest(tf_scatter, vtype, itype, repeat_indices,
                               updates_are_scalar)

  def testVariableRankUpdate(self):
    self._VariableRankTests(state_ops.scatter_update, False)

  def testVariableRankAdd(self):
    self._VariableRankTests(state_ops.scatter_add, False)

  def testVariableRankSub(self):
    self._VariableRankTests(state_ops.scatter_sub, False)

  def testVariableRankMul(self):
    self._VariableRankTests(state_ops.scatter_mul, False)

  def testVariableRankDiv(self):
    self._VariableRankTests(state_ops.scatter_div, False)

  def testVariableRankMin(self):
    self._VariableRankTests(state_ops.scatter_min, False)

  def testVariableRankMax(self):
    self._VariableRankTests(state_ops.scatter_max, False)

  def testRepeatIndicesAdd(self):
    self._VariableRankTests(state_ops.scatter_add, True)

  def testRepeatIndicesSub(self):
    self._VariableRankTests(state_ops.scatter_sub, True)

  def testRepeatIndicesMul(self):
    self._VariableRankTests(state_ops.scatter_mul, True)

  def testRepeatIndicesDiv(self):
    self._VariableRankTests(state_ops.scatter_div, True)

  def testRepeatIndicesMin(self):
    self._VariableRankTests(state_ops.scatter_min, True)

  def testRepeatIndicesMax(self):
    self._VariableRankTests(state_ops.scatter_max, True)

  def testVariableRankUpdateScalar(self):
    self._VariableRankTests(state_ops.scatter_update, False, True)

  def testVariableRankAddScalar(self):
    self._VariableRankTests(state_ops.scatter_add, False, True)

  def testVariableRankSubScalar(self):
    self._VariableRankTests(state_ops.scatter_sub, False, True)

  def testVariableRankMulScalar(self):
    self._VariableRankTests(state_ops.scatter_mul, False, True)

  def testVariableRankDivScalar(self):
    self._VariableRankTests(state_ops.scatter_div, False, True)

  def testVariableRankMinScalar(self):
    self._VariableRankTests(state_ops.scatter_min, False, True)

  def testVariableRankMaxScalar(self):
    self._VariableRankTests(state_ops.scatter_max, False, True)

  def testRepeatIndicesAddScalar(self):
    self._VariableRankTests(state_ops.scatter_add, True, True)

  def testRepeatIndicesSubScalar(self):
    self._VariableRankTests(state_ops.scatter_sub, True, True)

  def testRepeatIndicesMulScalar(self):
    self._VariableRankTests(state_ops.scatter_mul, True, True)

  def testRepeatIndicesDivScalar(self):
    self._VariableRankTests(state_ops.scatter_div, True, True)

  def testRepeatIndicesMinScalar(self):
    self._VariableRankTests(state_ops.scatter_min, True, True)

  def testRepeatIndicesMaxScalar(self):
    self._VariableRankTests(state_ops.scatter_max, True, True)

  def testBooleanScatterUpdate(self):
    if not test.is_gpu_available():
      with self.session(use_gpu=False):
        var = variables.Variable([True, False])
        update0 = state_ops.scatter_update(var, 1, True)
        update1 = state_ops.scatter_update(
            var, constant_op.constant(
                0, dtype=dtypes.int64), False)
        self.evaluate(var.initializer)

        self.evaluate([update0, update1])

        self.assertAllEqual([False, True], self.evaluate(var))

  def testScatterOutOfRangeCpu(self):
    for op, _ in _TF_OPS_TO_NUMPY.items():
      params = np.array([1, 2, 3, 4, 5, 6]).astype(np.float32)
      updates = np.array([-3, -4, -5]).astype(np.float32)
      if not test.is_gpu_available():
        with self.session(use_gpu=False):
          ref = variables.Variable(params)
          self.evaluate(ref.initializer)

          # Indices all in range, no problem.
          indices = np.array([2, 0, 5])
          self.evaluate(op(ref, indices, updates))

          # Test some out of range errors.
          indices = np.array([-1, 0, 5])
          with self.assertRaisesOpError(
              r'indices\[0\] = -1 is not in \[0, 6\)'):
            self.evaluate(op(ref, indices, updates))

          indices = np.array([2, 0, 6])
          with self.assertRaisesOpError(r'indices\[2\] = 6 is not in \[0, 6\)'):
            self.evaluate(op(ref, indices, updates))

  # TODO(fpmc): Re-enable this test when gpu_pip test actually runs on a GPU.
  def _disabledTestScatterOutOfRangeGpu(self):
    if test.is_gpu_available():
      return
    for op, _ in _TF_OPS_TO_NUMPY.items():
      params = np.array([1, 2, 3, 4, 5, 6]).astype(np.float32)
      updates = np.array([-3, -4, -5]).astype(np.float32)
      # With GPU, the code ignores indices that are out of range.
      # We don't test the implementation; just test there's no failures.
      with test_util.force_gpu():
        ref = variables.Variable(params)
        self.evaluate(ref.initializer)

        # Indices all in range, no problem.
        indices = np.array([2, 0, 5])
        self.evaluate(op(ref, indices, updates))

        # Indices out of range should not fail.
        indices = np.array([-1, 0, 5])
        self.evaluate(op(ref, indices, updates))
        indices = np.array([2, 0, 6])
        self.evaluate(op(ref, indices, updates))

  @test_util.run_v1_only("ResrouceVariable has deterministic scatter "
                         "implementation")
  @test_util.run_cuda_only
  def testDeterminismExceptionThrowing(self):
    v = ref_variable.RefVariable(np.array([1., 2., 3.]))
    indices = np.array([0, 0, 0])
    updates = np.array([-3, -4, -5]).astype(np.float32)
    with test_util.deterministic_ops():
      with self.assertRaisesRegex(
          errors.UnimplementedError,
          "Determinism is not yet supported in GPU implementation of Scatter "
          "ops"):
        self.evaluate(state_ops.scatter_update(v, indices, updates))




if __name__ == '__main__':
  test.main()
