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

        self.frequency_label = QtWidgets.QLabel("Frequency: 0h 0m 0s")
        self.layout.addWidget(self.frequency_label)
        self.frequency_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.frequency_layout)

        self.frequency_hours = QtWidgets.QDial()
        self.frequency_hours.setRange(0, 59)
        self.frequency_hours.setWrapping(False)
        self.frequency_hours.setNotchesVisible(True)
        self.frequency_hours.valueChanged.connect(self.changeFrequency)
        self.frequency_layout.addWidget(self.frequency_hours)

        self.frequency_minutes = QtWidgets.QDial()
        self.frequency_minutes.setRange(0, 59)
        self.frequency_minutes.setWrapping(False)
        self.frequency_minutes.setNotchesVisible(True)
        self.frequency_minutes.valueChanged.connect(self.changeFrequency)
        self.frequency_layout.addWidget(self.frequency_minutes)

        self.frequency_seconds = QtWidgets.QDial()
        self.frequency_seconds.setRange(0, 59)
        self.frequency_seconds.setWrapping(False)
        self.frequency_seconds.setNotchesVisible(True)
        self.frequency_seconds.valueChanged.connect(self.changeFrequency)
        self.frequency_layout.addWidget(self.frequency_seconds)

        self.duration_label = QtWidgets.QLabel("Duration: 0h 0m 0s")
        self.layout.addWidget(self.duration_label)
        self.duration_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.duration_layout)

        self.duration_hours = QtWidgets.QDial()
        self.duration_hours.setRange(0, 59)
        self.duration_hours.setWrapping(False)
        self.duration_hours.setNotchesVisible(True)
        self.duration_hours.valueChanged.connect(self.changeDuration)
        self.duration_layout.addWidget(self.duration_hours)

        self.duration_minutes = QtWidgets.QDial()
        self.duration_minutes.setRange(0, 59)
        self.duration_minutes.setWrapping(False)
        self.duration_minutes.setNotchesVisible(True)
        self.duration_minutes.valueChanged.connect(self.changeDuration)
        self.duration_layout.addWidget(self.duration_minutes)

        self.duration_seconds = QtWidgets.QDial()
        self.duration_seconds.setRange(0, 59)
        self.duration_seconds.setWrapping(False)
        self.duration_seconds.setNotchesVisible(True)
        self.duration_seconds.valueChanged.connect(self.changeDuration)
        self.duration_layout.addWidget(self.duration_seconds)

        self.time_value = QtWidgets.QLCDNumber()
        self.time_value.setDigitCount(8)
        self.time_value.display("00:00:00")
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

    def changeFrequency(self, _):
        hours = self.frequency_hours.value()
        minutes = self.frequency_minutes.value()
        seconds = self.frequency_seconds.value()
        self.frequency_label.setText(f"Frequency: {hours}h {minutes}m {seconds}s")
        self.time_value.display(f"{hours:02}:{minutes:02}:{seconds:02}")

    def changeDuration(self, _):
        hours = self.duration_hours.value()
        minutes = self.duration_minutes.value()
        seconds = self.duration_seconds.value()
        self.duration_label.setText(f"Duration: {hours}h {minutes}m {seconds}s")

    def updateTimer(self, value):
        value -= 1
        hours, minutes = divmod(value, 3600)
        minutes, seconds = divmod(minutes, 60)
        self.time_value.display(f"{hours:02}:{minutes:02}:{seconds:02}")
        return value

    def toggleTime(self):
        if self.phase == 1:
            self.frequency = self.updateTimer(self.frequency)
            if self.frequency <= 0:
                self.frequency = (self.frequency_hours.value() * 3600 +
                                  self.frequency_minutes.value() * 60 +
                                  self.frequency_seconds.value())
                self.phase = 2
                self.alert.play()
        elif self.phase == 2:
            self.duration = self.updateTimer(self.duration)
            if self.duration <= 0:
                self.duration = (self.duration_hours.value() * 3600 +
                                 self.duration_minutes.value() * 60 +
                                 self.duration_seconds.value())
                self.phase = 1
                self.success.play()

    def startClock(self):
        self.frequency = (self.frequency_hours.value() * 3600 +
                          self.frequency_minutes.value() * 60 +
                          self.frequency_seconds.value())
        self.duration = (self.duration_hours.value() * 3600 +
                         self.duration_minutes.value() * 60 +
                         self.duration_seconds.value())
        if self.frequency == 0 and self.duration == 0:
            return
        self.phase = 1
        self.skip_button.setText("Skip\nBreak")
        self.start_button.setEnabled(False)
        self.frequency_minutes.setEnabled(False)
        self.frequency_seconds.setEnabled(False)
        self.duration_minutes.setEnabled(False)
        self.duration_seconds.setEnabled(False)
        self.skip_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.timer.start(1000)

    def skipClock(self):
        if self.phase == 1:
            self.frequency = (self.frequency_hours.value() * 3600 +
                              self.frequency_minutes.value() * 60 +
                              self.frequency_seconds.value())
            self.phase = 2
            self.skip_button.setText("Skip\nTask")
        elif self.phase == 2:
            self.duration = (self.duration_hours.value() * 3600 +
                             self.duration_minutes.value() * 60 +
                             self.duration_seconds.value())
            self.phase = 1
            self.skip_button.setText("Skip\nBreak")

    def stopClock(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.frequency_minutes.setEnabled(True)
        self.frequency_seconds.setEnabled(True)
        self.duration_minutes.setEnabled(True)
        self.duration_seconds.setEnabled(True)
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
