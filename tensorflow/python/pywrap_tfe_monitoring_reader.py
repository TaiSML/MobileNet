# Copyright 2023 The TensorFlow Authors. All Rights Reserved.
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
"""Python module for TFE ops and functions exported by pybind11.

This module is created because we are splitting out eager bindings from
pywrap_tensorflow. This is causing some issues where Graphs are not properly
initialized when running eager code. Once the graph architecture has been
removed from pywrap_tensorflow as well, we can remove this file.
"""

# pylint: disable=invalid-import-order,g-bad-import-order, wildcard-import, unused-import
from tensorflow.python._pywrap_tfe_monitoring_reader import *
