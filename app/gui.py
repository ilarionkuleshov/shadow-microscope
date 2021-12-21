import os
import time
from urllib.request import urlretrieve

from PySide6.QtWidgets import QMainWindow, QWidget, QTabWidget, QPushButton, QVBoxLayout, QFileDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl


class MainWindow(QMainWindow):

	def __init__(self):
		super(MainWindow, self).__init__()

		self.setWindowTitle('Shadow microscope')
		self.resize(640, 480)

		tab_widget = QTabWidget()
		tab_widget.addTab(StreamTab('http://192.168.0.107'), 'Live video')

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
