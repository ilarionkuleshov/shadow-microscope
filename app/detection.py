from math import tan, pi

import cv2
import numpy as np

from tflite_runtime.interpreter import Interpreter


class ObjectDetector:

	def __init__(self, tflite_model, threshold, image_res):
		self.interpreter = Interpreter(model_path=tflite_model)
		self.interpreter.allocate_tensors()

		self.input_details = self.interpreter.get_input_details()
		self.output_details = self.interpreter.get_output_details()
		self.height = self.input_details[0]['shape'][1]
		self.width = self.input_details[0]['shape'][2]

		self.floating_model = (self.input_details[0]['dtype'] == np.float32)

		self.input_mean = 127.5
		self.input_std = 127.5

		self.threshold = threshold
		self.res_x, self.res_y = image_res

	def get_contours(self, image):
		resized_image = cv2.resize(image.copy(), (self.width, self.height))
		input_data = np.expand_dims(resized_image, axis=0)

		if self.floating_model:
			input_data = (np.float32(input_data) - self.input_mean) / self.input_std

		self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
		self.interpreter.invoke()

		boxes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
		scores = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

		contours = []

		for i in range(len(scores)):
			if scores[i] >= self.threshold and scores[i] <= 1.0:
				y_min = int(max(1, (boxes[i][0] * self.res_y)))
				x_min = int(max(1, (boxes[i][1] * self.res_x)))
				y_max = int(min(self.res_y, (boxes[i][2] * self.res_y)))
				x_max = int(min(self.res_x, (boxes[i][3] * self.res_x)))

				contours.append([x_min, y_min, x_max, y_max])

		return contours


def get_real_size(size_in_px, av_res_in_px, chief_ray_angle, L, R, n1, n2):
	H = 2*L*tan((chief_ray_angle)*pi/180)*size_in_px/av_res_in_px

	F = (n2*R)/(n1-n2)
	h = (H*F)/(L-R-F)

	return h
