import os
import sys

os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
import tensorflow as tf

import onnx2tf
import onnx2tf.onnx2tf
import onnx2tf.utils.common_functions

dummy_fn = lambda *args, **kwargs: np.zeros((1, 3, 1024, 1024), dtype=np.float32)
onnx2tf.onnx2tf.download_test_image_data = dummy_fn
onnx2tf.utils.common_functions.download_test_image_data = dummy_fn
if hasattr(onnx2tf, "download_test_image_data"):
    onnx2tf.download_test_image_data = dummy_fn

input_onnx = r"C:\Users\ZBook 4K\Desktop\Lab 5\LASTMODEL\best(1).onnx"
output_folder = r"C:\Users\ZBook 4K\Desktop\Lab 5\LASTMODEL\tflite_out"

print(f"Converting {input_onnx} with static batch=1 to TFLite...")
onnx2tf.convert(
    input_onnx_file_path=input_onnx,
    output_folder_path=output_folder,
    batch_size=1,
    overwrite_input_shape=['images:1,3,1024,1024'],
    output_integer_quantized_tflite=False,
    copy_onnx_input_output_names_to_tflite=True,
    check_onnx_tf_outputs_elementwise_close=False,
    non_verbose=True
)

print("Conversion complete!")
