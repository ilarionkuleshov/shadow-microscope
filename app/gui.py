import os
import time
from urllib.request import urlretrieve

import cv2

from PySide6.QtWidgets import QMainWindow, QWidget, QTabWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QFileDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from PySide6.QtGui import QPixmap

from detection import ObjectDetector


class MainWindow(QMainWindow):

	def __init__(self):
		super(MainWindow, self).__init__()

		self.setWindowTitle('Shadow microscope')
		self.resize(800, 600)

		tab_widget = QTabWidget()
		tab_widget.addTab(StreamTab('http://192.168.0.107'), 'Live video')
		tab_widget.addTab(ProcessingTab('neural-network/model_100k.tflite', 0.4, (800, 600)), 'Image processing')

		self.setCentralWidget(tab_widget)


class StreamTab(QWidget):

	def __init__(self, url):
		super(StreamTab, self).__init__()

		self.url = url

		self.web_view = QWebEngineView()
		self.web_view.load(QUrl(f"{url}/cam.mjpeg"))

		save_frame_but = QPushButton('Save current frame')
		save_frame_but.clicked.connect(self.save_frame)

		layout = QVBoxLayout()
		layout.addWidget(self.web_view)
		layout.addWidget(save_frame_but)

		self.setLayout(layout)

	def save_frame(self):
		self.web_view.stop()
		time.sleep(0.5)

		urlretrieve(f"{self.url}/cam.jpg", 'temp.jpg')

		save_file_name = QFileDialog.getSaveFileName(filter='*.jpg')

		if save_file_name[0] != '':
			if save_file_name[0].split('.')[-1] == 'jpg':
				save_path = save_file_name[0]
			else:
				save_path = f"{save_file_name[0]}{save_file_name[1][1:]}"

			os.replace('temp.jpg', save_path)

		self.web_view.reload()


class ProcessingTab(QWidget):

	def __init__(self, tflite_model, threshold, image_res):
		super(ProcessingTab, self).__init__()

		self.detector = ObjectDetector(tflite_model, threshold, image_res)

		self.path_input = QLineEdit(placeholderText='Path to image...')

		path_button = QPushButton('...')
		path_button.clicked.connect(self.path_button_click)

		detect_button = QPushButton('Start processing')
		detect_button.clicked.connect(self.detect_button_click)

		h_layout = QHBoxLayout()
		h_layout.addWidget(self.path_input)
		h_layout.addWidget(path_button)
		h_layout.addWidget(detect_button)

		h_widget = QWidget()
		h_widget.setLayout(h_layout)

		self.image_label = QLabel() 
		self.update_image('extra-files/blank.png')

		v_layout = QVBoxLayout()
		v_layout.addWidget(h_widget)
		v_layout.addWidget(self.image_label)

		self.setLayout(v_layout)

	def path_button_click(self):
		image_path = QFileDialog.getOpenFileName(filter='*.jpg')
		self.path_input.setText(image_path[0])

	def detect_button_click(self):
		image = cv2.imread(self.path_input.text())

		for contour in self.detector.get_contours(image):
			x_min, y_min, x_max, y_max = contour
			image = cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 1)
			cv2.imwrite('extra-files/temp.jpg', image)

		self.update_image('extra-files/temp.jpg')

	def update_image(self, image_path):
		image_pixmap = QPixmap(image_path)
		self.image_label.setPixmap(image_pixmap)
