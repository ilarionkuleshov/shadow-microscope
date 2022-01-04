import os
import time
from urllib.request import urlretrieve

import cv2

from PySide6.QtWidgets import QMainWindow, QWidget, QTabWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QFileDialog, QToolTip
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, QPoint
from PySide6.QtGui import QFont, QPixmap

from detection import ObjectDetector


BASIC_FONT = QFont()
BASIC_FONT.setPixelSize(13)

BOLD_FONT = QFont()
BOLD_FONT.setPixelSize(14)
BOLD_FONT.setBold(True)


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
		save_frame_but.setFont(BOLD_FONT)
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
		self.path_input.setFont(BASIC_FONT)

		path_button = QPushButton('...')
		path_button.setFont(BASIC_FONT)
		path_button.clicked.connect(self.path_button_click)

		detect_button = QPushButton('Start processing')
		detect_button.setFont(BOLD_FONT)
		detect_button.clicked.connect(self.detect_button_click)

		h_layout = QHBoxLayout()
		h_layout.addWidget(self.path_input)
		h_layout.addWidget(path_button)
		h_layout.addWidget(detect_button)

		h_widget = QWidget()
		h_widget.setLayout(h_layout)

		self.image_widget = ImageWithInfo()

		v_layout = QVBoxLayout()
		v_layout.addWidget(h_widget)
		v_layout.addWidget(self.image_widget)

		self.setLayout(v_layout)

	def path_button_click(self):
		image_path = QFileDialog.getOpenFileName(filter='*.jpg')
		self.path_input.setText(image_path[0])

	def detect_button_click(self):
		image = cv2.imread(self.path_input.text())
		contours = self.detector.get_contours(image)

		for contour in contours:
			x_min, y_min, x_max, y_max = contour
			image = cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 1)

			cv2.imwrite('extra-files/temp.jpg', image)

		self.image_widget.update_image('extra-files/temp.jpg', contours)


class ImageWithInfo(QWidget):

	def __init__(self):
		super(ImageWithInfo, self).__init__()

		self.image_label = QLabel()

		self.contours = []
		QToolTip.setFont(BASIC_FONT)

		self.update_image('extra-files/blank.png', [])

		self.image_label.setMouseTracking(True)
		self.image_label.mouseMoveEvent = self.mouse_event

		self.current_mouse_pos = (None, None)

		layout = QVBoxLayout()
		layout.addWidget(self.image_label)

		self.setLayout(layout)

	def update_image(self, image_path, contours):
		image_pixmap = QPixmap(image_path)
		self.image_label.setPixmap(image_pixmap)

		self.contours = contours

	def mouse_event(self, event):
		mouse_pos = event.pos()
		mouse_x, mouse_y = mouse_pos.x(), mouse_pos.y()

		for contour in self.contours:
			x_min, y_min, x_max, y_max = contour

			if (mouse_x >= x_min and mouse_x <= x_max) and (mouse_y >= y_min and mouse_y <= y_max):
				self.current_mouse_pos = mouse_x, mouse_y

				tooltip_point = -self.image_label.mapFromGlobal(self.image_label.pos())+mouse_pos+QPoint(10, 10)
				tooltip_text = f"Coordinates:\nx1 = {x_min}; y1 = {y_min}\nx2 = {x_max}; y2 = {y_max}"
				QToolTip.showText(tooltip_point, tooltip_text)

		if mouse_x != self.current_mouse_pos[0] or mouse_y != self.current_mouse_pos[1]:
			QToolTip.hideText()
