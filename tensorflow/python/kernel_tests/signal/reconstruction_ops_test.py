# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
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
"""Tests for reconstruction_ops."""

from absl.testing import parameterized
import numpy as np

from tensorflow.python.eager import context
from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import test_util
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import array_ops_stack
from tensorflow.python.ops import gradient_checker_v2
from tensorflow.python.ops import gradients_impl
from tensorflow.python.ops import math_ops
from tensorflow.python.ops.signal import reconstruction_ops
from tensorflow.python.platform import test


@test_util.run_all_in_graph_and_eager_modes
class ReconstructionOpsTest(test.TestCase, parameterized.TestCase):

  def __init__(self, *args, **kwargs):
    super(ReconstructionOpsTest, self).__init__(*args, **kwargs)
    self.batch_size = 3
    self.frames = 3
    self.samples = 5

    self.bases = np.array(range(2, 5))
    exponents = np.array(range(self.frames * self.samples))
    powers = np.power(self.bases[:, np.newaxis], exponents[np.newaxis, :])

    self.powers = np.reshape(powers, [self.batch_size, self.frames,
                                      self.samples])
    self.frame_hop = 2

    # Hand computed example using powers of unique numbers: this is easily
    # verified.
    self.expected_string = ["1", "10", "100100", "1001000", "10010010000",
                            "100100000000", "1001000000000", "10000000000000",
                            "100000000000000"]

  def test_all_ones(self):
    signal = array_ops.ones([3, 5])
    reconstruction = reconstruction_ops.overlap_and_add(signal, 2)
    self.assertEqual(reconstruction.shape.as_list(), [9])
    expected_output = np.array([1, 1, 2, 2, 3, 2, 2, 1, 1])
    self.assertAllClose(reconstruction, expected_output)

  def test_unknown_shapes(self):
    # This test uses placeholders and does not work in Eager mode.
    if context.executing_eagerly():
      return
    signal = array_ops.placeholder_with_default(
        np.ones((4, 3, 5)).astype(np.int32), shape=[None, None, None])
    frame_step = array_ops.placeholder_with_default(2, shape=[])
    reconstruction = reconstruction_ops.overlap_and_add(signal, frame_step)
    self.assertEqual(reconstruction.shape.as_list(), [None, None])
    expected_output = np.array([[1, 1, 2, 2, 3, 2, 2, 1, 1]] * 4)
    self.assertAllClose(reconstruction, expected_output)

  def test_unknown_rank(self):
    # This test uses placeholders and does not work in eager mode.
    if context.executing_eagerly():
      return
    signal = array_ops.placeholder_with_default(
        np.ones((4, 3, 5)).astype(np.int32), shape=None)
    frame_step = array_ops.placeholder_with_default(2, shape=[])
    reconstruction = reconstruction_ops.overlap_and_add(signal, frame_step)

    self.assertEqual(reconstruction.shape, None)
    expected_output = np.array([[1, 1, 2, 2, 3, 2, 2, 1, 1]] * 4)
    self.assertAllClose(reconstruction, expected_output)

  def test_fast_path(self):
    # This test uses tensor names and does not work in eager mode.
    if context.executing_eagerly():
      return
    signal = array_ops.ones([3, 5])
    frame_step = 5
    reconstruction = reconstruction_ops.overlap_and_add(signal, frame_step)
    self.assertEqual(reconstruction.name, "overlap_and_add/fast_path:0")
    expected_output = np.ones([15])
    self.assertAllClose(reconstruction, expected_output)

  @parameterized.parameters(
      # All hop lengths on a frame length of 2.
      (2, [1, 5, 9, 6], 1),
      (2, [1, 2, 3, 4, 5, 6], 2),

      # All hop lengths on a frame length of 3.
      (3, [1, 6, 15, 14, 9], 1),
      (3, [1, 2, 7, 5, 13, 8, 9], 2),
      (3, [1, 2, 3, 4, 5, 6, 7, 8, 9], 3),

      # All hop lengths on a frame length of 4.
      (4, [1, 7, 18, 21, 19, 12], 1),
      (4, [1, 2, 8, 10, 16, 18, 11, 12], 2),
      (4, [1, 2, 3, 9, 6, 7, 17, 10, 11, 12], 3),
      (4, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 4))
  def test_simple(self, frame_length, expected, frame_hop):
    def make_input(frame_length, num_frames=3):
      """Generate a tensor of num_frames frames of frame_length."""
      return np.reshape(np.arange(1, num_frames * frame_length + 1),
                        (-1, frame_length))
    signal = make_input(frame_length)
    reconstruction = reconstruction_ops.overlap_and_add(
        np.array(signal), frame_hop)
    expected_output = np.array(expected)
    self.assertAllClose(reconstruction, expected_output)

  def test_powers(self):
    signal = constant_op.constant(np.squeeze(self.powers[0, :, :]),
                                  dtype=dtypes.int64)
    reconstruction = reconstruction_ops.overlap_and_add(signal, self.frame_hop)

    output = self.evaluate(reconstruction)
    string_output = [np.base_repr(x, self.bases[0]) for x in output]
    self.assertEqual(string_output, self.expected_string)

  def test_batch(self):
    signal = constant_op.constant(self.powers, dtype=dtypes.int64)
    reconstruction = reconstruction_ops.overlap_and_add(signal, self.frame_hop)

    output = self.evaluate(reconstruction)

    accumulator = True
    for i in range(self.batch_size):
      string_output = [np.base_repr(x, self.bases[i]) for x in output[i, :]]
      accumulator = accumulator and (string_output == self.expected_string)

    self.assertTrue(accumulator)

  def test_one_element_batch(self):
    input_matrix = np.squeeze(self.powers[0, :, :])
    input_matrix = input_matrix[np.newaxis, :, :].astype(float)
    signal = constant_op.constant(input_matrix, dtype=dtypes.float32)
    reconstruction = reconstruction_ops.overlap_and_add(signal, self.frame_hop)

    output = self.evaluate(reconstruction)

    string_output = [np.base_repr(int(x), self.bases[0]) for x in
                     np.squeeze(output)]

    self.assertEqual(output.shape, (1, 9))
    self.assertEqual(string_output, self.expected_string)

  @parameterized.parameters(
      ((1, 128), 1),
      ((5, 35), 17),
      ((10, 128), 128),
      ((2, 10, 128), 127),
      ((2, 2, 10, 128), 126),
      ((2, 2, 2, 10, 128), 125))
  def test_gradient(self, shape, frame_hop):
    # TODO(rjryan): Eager gradient tests.
    if context.executing_eagerly():
      return
    signal = array_ops.zeros(shape)
    reconstruction = reconstruction_ops.overlap_and_add(signal, frame_hop)
    loss = math_ops.reduce_sum(reconstruction)
    # Increasing any sample in the input frames by one will increase the sum
    # of all the samples in the reconstruction by 1, so the gradient should
    # be all ones, no matter the shape or hop.
    gradient = self.evaluate(gradients_impl.gradients([loss], [signal])[0])
    self.assertTrue((gradient == 1.0).all())

  def test_gradient_batch(self):
    # TODO(rjryan): Eager gradient tests.
    if context.executing_eagerly():
      return
    signal = array_ops.zeros((2, 10, 10))
    frame_hop = 10
    reconstruction = reconstruction_ops.overlap_and_add(signal, frame_hop)

    # Multiply the first batch-item's reconstruction by zeros. This will block
    # gradient from flowing into the first batch item from the loss. Multiply
    # the second batch item by the integers from 0 to 99. Since there is zero
    # overlap, the gradient for this batch item will be 0-99 shaped as (10,
    # 10).
    reconstruction *= array_ops_stack.stack(
        [array_ops.zeros((100,)),
         math_ops.cast(math_ops.range(100), dtypes.float32)])
    loss = math_ops.reduce_sum(reconstruction)

    # Verify that only the second batch item receives gradient.
    gradient = self.evaluate(gradients_impl.gradients([loss], [signal])[0])
    expected_gradient = np.stack([
        np.zeros((10, 10)),
        np.reshape(np.arange(100).astype(np.float32), (10, 10))])
    self.assertAllEqual(expected_gradient, gradient)

  def test_gradient_numerical(self):
    shape = (2, 10, 10)
    framed_signal = array_ops.zeros(shape)
    frame_hop = 10
    def f(signal):
      return reconstruction_ops.overlap_and_add(signal, frame_hop)
    ((jacob_t,), (jacob_n,)) = gradient_checker_v2.compute_gradient(
        f, [framed_signal])
    self.assertAllClose(jacob_t, jacob_n)


if __name__ == "__main__":
  test.main()
