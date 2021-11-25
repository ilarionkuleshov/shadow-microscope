from PySide6.QtWidgets import QMainWindow, QWidget, QTabWidget, QPushButton, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl


class MainWindow(QMainWindow):

	def __init__(self):
		super(MainWindow, self).__init__()

		self.setWindowTitle('Shadow microscope')
		self.resize(640, 480)

		tab_widget = QTabWidget()
		tab_widget.addTab(StreamTab('http://192.168.0.104/cam.mjpeg'), 'Live video')

		self.setCentralWidget(tab_widget)


class StreamTab(QWidget):

	def __init__(self, stream_url):
		super(StreamTab, self).__init__()

		web_view = QWebEngineView()
		web_view.load(QUrl(stream_url))

		get_frame_but = QPushButton('Get current frame')
		get_frame_but.clicked.connect(self.get_frame)

		layout = QVBoxLayout()
		layout.addWidget(web_view)
		layout.addWidget(get_frame_but)

		self.setLayout(layout)

	def get_frame(self):
		pass
