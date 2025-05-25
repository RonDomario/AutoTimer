from PyQt6 import QtGui, QtWidgets, QtCore, QtMultimedia
import sys


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.position = None
        self.always_on_top = True
        self.duration = None
        self.frequency = None
        self.window_width = 200
        self.window_height = 300
        self.phase = 1
        if QtCore.QFile.exists("media/themes/cucumber.png"):
            self.cucumber = QtGui.QPixmap("media/themes/cucumber.png")
        else:
            self.cucumber = QtGui.QPixmap(self.window_width, self.window_height)
            self.cucumber.fill(QtGui.QColor("gray"))
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, self.always_on_top)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.window_width, self.window_height)

        self.central = QtWidgets.QLabel()
        self.central.setPixmap(self.cucumber)
        self.central.setScaledContents(True)
        self.setCentralWidget(self.central)
        self.layout = QtWidgets.QVBoxLayout()
        self.central.setLayout(self.layout)
        self.top_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        self.always_on_top_checkbox = QtWidgets.QCheckBox("Always on top")
        self.always_on_top_checkbox.setChecked(True)
        self.always_on_top_checkbox.stateChanged.connect(self.changeAlwaysOnTop)
        self.top_layout.addWidget(self.always_on_top_checkbox)
        self.info_button = QtWidgets.QPushButton("Info")
        self.info_button.clicked.connect(self.showInfo)
        self.top_layout.addWidget(self.info_button)

        self.opacity_label = QtWidgets.QLabel("Opacity: 100%")
        self.layout.addWidget(self.opacity_label)
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(20)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.changeOpacity)
        self.layout.addWidget(self.opacity_slider)

        self.frequency_label = QtWidgets.QLabel("Frequency: 1m")
        self.layout.addWidget(self.frequency_label)
        self.frequency_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.frequency_slider.setMinimum(1)
        self.frequency_slider.setMaximum(60)
        self.frequency_slider.setValue(1)
        self.frequency_slider.valueChanged.connect(self.changeFrequency)
        self.layout.addWidget(self.frequency_slider)

        self.duration_label = QtWidgets.QLabel("Duration: 1m")
        self.layout.addWidget(self.duration_label)
        self.duration_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.duration_slider.setMinimum(1)
        self.duration_slider.setMaximum(60)
        self.duration_slider.setValue(1)
        self.duration_slider.valueChanged.connect(self.changeDuration)
        self.layout.addWidget(self.duration_slider)

        self.time_value = QtWidgets.QLCDNumber()
        self.time_value.display("01:00")
        self.layout.addWidget(self.time_value)

        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.bottom_layout)
        self.start_button = QtWidgets.QPushButton("Start\nTimer")
        self.start_button.clicked.connect(self.startClock)
        self.bottom_layout.addWidget(self.start_button)

        self.skip_button = QtWidgets.QPushButton("Skip\nBreak")
        self.skip_button.setEnabled(False)
        self.skip_button.clicked.connect(self.skipClock)
        self.bottom_layout.addWidget(self.skip_button)

        self.stop_button = QtWidgets.QPushButton("Stop\nTimer")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stopClock)
        self.bottom_layout.addWidget(self.stop_button)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.toggleTime)

        self.alert = QtMultimedia.QSoundEffect()
        if QtCore.QFile.exists("media/sounds/alert.wav"):
            self.alert.setSource(QtCore.QUrl.fromLocalFile("media/sounds/alert.wav"))
            self.alert.setVolume(0.3)

        self.success = QtMultimedia.QSoundEffect()
        if QtCore.QFile.exists("media/sounds/success.wav"):
            self.success.setSource(QtCore.QUrl.fromLocalFile("media/sounds/success.wav"))
            self.success.setVolume(0.3)

    def changeAlwaysOnTop(self):
        self.always_on_top = self.always_on_top_checkbox.isChecked()
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, self.always_on_top)
        self.show()

    def showInfo(self):
        try:
            with open("info.txt", "r") as file:
                info = "".join(file.readlines())
        except FileNotFoundError:
            info = ""
        QtWidgets.QMessageBox.information(self, "Info", info)

    def changeOpacity(self, value):
        self.opacity_label.setText(f"Opacity: {value}%")
        self.setWindowOpacity(value / 100)

    def changeFrequency(self, value):
        self.frequency_label.setText(f"Frequency: {value}m")
        self.time_value.display(f"{str(value).zfill(2)}:00")

    def changeDuration(self, value):
        self.duration_label.setText(f"Duration: {value}m")

    def updateTimer(self, value):
        value -= 1
        minutes, seconds = divmod(value, 60)
        self.time_value.display(f"{str(minutes).zfill(2)}:{str(seconds).zfill(2)}")
        return value

    def toggleTime(self):
        if self.phase == 1:
            self.frequency = self.updateTimer(self.frequency)
            if self.frequency <= 0:
                self.alert.play()
                self.phase = 2
                self.frequency = self.frequency_slider.value() * 60
        elif self.phase == 2:
            self.duration = self.updateTimer(self.duration)
            if self.duration <= 0:
                self.success.play()
                self.phase = 1
                self.duration = self.duration_slider.value() * 60

    def startClock(self):
        self.phase = 1
        self.skip_button.setText("Skip\nBreak")
        self.frequency = self.frequency_slider.value() * 60
        self.duration = self.duration_slider.value() * 60
        self.start_button.setEnabled(False)
        self.frequency_slider.setEnabled(False)
        self.duration_slider.setEnabled(False)
        self.skip_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.timer.start(1000)

    def skipClock(self):
        if self.phase == 1:
            self.skip_button.setText("Skip\nTask")
            self.phase = 2
            self.frequency = self.frequency_slider.value() * 60
        elif self.phase == 2:
            self.skip_button.setText("Skip\nBreak")
            self.phase = 1
            self.duration = self.duration_slider.value() * 60

    def stopClock(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.frequency_slider.setEnabled(True)
        self.duration_slider.setEnabled(True)
        self.skip_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.position is not None:
            self.move(event.globalPosition().toPoint() - self.position)

    def mouseReleaseEvent(self, event):
        self.position = None


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
