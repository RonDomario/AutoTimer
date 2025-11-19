from PyQt6 import QtGui, QtWidgets, QtCore, QtMultimedia
from os.path import join, abspath, exists
import sys
from pathlib import Path


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = abspath(".")
    return join(base_path, relative_path)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.path = Path(__file__)
        self.path_sounds = self.path.parent / "media/sounds"
        self.path_themes = self.path.parent / "media/themes"
        self.path_icon = self.path.parent / "media/icon.png"
        self.path_config = self.path.parent / "config.ini"
        self.position = None
        self.always_on_top = True
        self.work_duration = 0
        self.break_duration = 0
        self.work_volume = 100
        self.break_volume = 100
        self.window_width = 200
        self.window_height = 300
        self.phase = 1
        self.theme = None
        self.theme_names = {"apple", "coconut", "cucumber", "watermelon"}
        self.theme_name = "cucumber"
        self.settings = None
        self.loadConfig()

        if exists(self.path_themes / f"theme_{self.theme_name}.png"):
            self.theme = QtGui.QPixmap(str(self.path_themes / f"theme_{self.theme_name}.png"))
        else:
            self.theme = QtGui.QPixmap(self.window_width, self.window_height)
            self.theme.fill(QtGui.QColor("gray"))

        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, self.always_on_top)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.window_width, self.window_height)

        self.central = QtWidgets.QLabel()
        self.central.setPixmap(self.theme)
        self.central.setScaledContents(True)
        self.setCentralWidget(self.central)
        self.layout = QtWidgets.QVBoxLayout()
        self.central.setLayout(self.layout)
        self.top_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        self.settings_button = QtWidgets.QPushButton("Settings")
        self.settings_button.clicked.connect(self.openSettings)
        self.top_layout.addWidget(self.settings_button)
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

        self.work_label = QtWidgets.QLabel("Work: 0h 0m 0s")
        self.layout.addWidget(self.work_label)
        self.work_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.work_layout)

        self.work_hours = QtWidgets.QDial()
        self.work_hours.setRange(0, 59)
        self.work_hours.setWrapping(False)
        self.work_hours.setNotchesVisible(True)
        self.work_hours.valueChanged.connect(self.changeWorkDuration)
        self.work_layout.addWidget(self.work_hours)

        self.work_minutes = QtWidgets.QDial()
        self.work_minutes.setRange(0, 59)
        self.work_minutes.setWrapping(False)
        self.work_minutes.setNotchesVisible(True)
        self.work_minutes.valueChanged.connect(self.changeWorkDuration)
        self.work_layout.addWidget(self.work_minutes)

        self.work_seconds = QtWidgets.QDial()
        self.work_seconds.setRange(0, 59)
        self.work_seconds.setWrapping(False)
        self.work_seconds.setNotchesVisible(True)
        self.work_seconds.valueChanged.connect(self.changeWorkDuration)
        self.work_layout.addWidget(self.work_seconds)

        self.brake_label = QtWidgets.QLabel("Break: 0h 0m 0s")
        self.layout.addWidget(self.brake_label)
        self.break_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.break_layout)

        self.break_hours = QtWidgets.QDial()
        self.break_hours.setRange(0, 59)
        self.break_hours.setWrapping(False)
        self.break_hours.setNotchesVisible(True)
        self.break_hours.valueChanged.connect(self.changeBreakDuration)
        self.break_layout.addWidget(self.break_hours)

        self.break_minutes = QtWidgets.QDial()
        self.break_minutes.setRange(0, 59)
        self.break_minutes.setWrapping(False)
        self.break_minutes.setNotchesVisible(True)
        self.break_minutes.valueChanged.connect(self.changeBreakDuration)
        self.break_layout.addWidget(self.break_minutes)

        self.break_seconds = QtWidgets.QDial()
        self.break_seconds.setRange(0, 59)
        self.break_seconds.setWrapping(False)
        self.break_seconds.setNotchesVisible(True)
        self.break_seconds.valueChanged.connect(self.changeBreakDuration)
        self.break_layout.addWidget(self.break_seconds)

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

        self.work_alert = QtMultimedia.QSoundEffect()
        if exists(resource_path("media/sounds/alert.wav")):
            self.work_alert.setSource(QtCore.QUrl.fromLocalFile(resource_path("media/sounds/alert.wav")))
            self.work_alert.setVolume(self.work_volume / 100)

        self.break_alert = QtMultimedia.QSoundEffect()
        if exists(resource_path("media/sounds/success.wav")):
            self.break_alert.setSource(QtCore.QUrl.fromLocalFile(resource_path("media/sounds/success.wav")))
            self.break_alert.setVolume(self.break_volume / 100)

    def loadConfig(self):
        if exists(self.path_config):
            self.settings = QtCore.QSettings(str(self.path_config), QtCore.QSettings.Format.IniFormat)
            self.always_on_top = self.settings.value("app/always_on_top", type=bool)
            self.work_volume = self.settings.value("app/work_volume", type=int)
            self.break_volume = self.settings.value("app/break_volume", type=int)
            self.theme_name = self.settings.value("app/theme_name", type=str)
        else:
            self.createConfig()

    def createConfig(self):
        self.path_config.touch()
        self.settings = QtCore.QSettings(str(self.path_config), QtCore.QSettings.Format.IniFormat)
        self.settings.setValue("app/always_on_top", self.always_on_top)
        self.settings.setValue("app/work_volume", self.work_volume)
        self.settings.setValue("app/break_volume", self.break_volume)
        self.settings.setValue("app/theme_name", self.theme_name)

    def saveConfig(self):
        self.settings.setValue("app/always_on_top", self.always_on_top)
        self.settings.setValue("app/work_volume", self.work_volume)
        self.settings.setValue("app/break_volume", self.break_volume)
        self.settings.setValue("app/theme_name", self.theme_name)

    def openSettings(self):
        settings = Settings(self, self.always_on_top, self.work_volume, self.break_volume, self.theme)
        settings.exec()
        self.always_on_top, self.work_volume, self.break_volume, self.theme = settings.settings()
        self.saveConfig()
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, self.always_on_top)
        self.show()
        self.work_alert.setVolume(self.work_volume / 100)
        self.break_alert.setVolume(self.break_volume / 100)

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

    def changeWorkDuration(self, _):
        hours = self.work_hours.value()
        minutes = self.work_minutes.value()
        seconds = self.work_seconds.value()
        self.work_label.setText(f"Frequency: {hours}h {minutes}m {seconds}s")
        self.time_value.display(f"{hours:02}:{minutes:02}:{seconds:02}")

    def changeBreakDuration(self, _):
        hours = self.break_hours.value()
        minutes = self.break_minutes.value()
        seconds = self.break_seconds.value()
        self.brake_label.setText(f"Duration: {hours}h {minutes}m {seconds}s")

    @staticmethod
    def timeToHMS(time: int):
        hours, minutes = divmod(time, 3600)
        minutes, seconds = divmod(minutes, 60)
        return hours, minutes, seconds

    def updateTimer(self, value):
        value -= 1
        hours, minutes, seconds = self.timeToHMS(value)
        self.time_value.display(f"{hours:02}:{minutes:02}:{seconds:02}")
        return value

    def toggleTime(self):
        if self.phase == 1:
            self.work_duration = self.updateTimer(self.work_duration)
            if self.work_duration <= 0:
                self.work_duration = (self.work_hours.value() * 3600 +
                                      self.work_minutes.value() * 60 +
                                      self.work_seconds.value())
                self.phase = 2
                self.work_alert.play()
        elif self.phase == 2:
            self.break_duration = self.updateTimer(self.break_duration)
            if self.break_duration <= 0:
                self.break_duration = (self.break_hours.value() * 3600 +
                                       self.break_minutes.value() * 60 +
                                       self.break_seconds.value())
                self.phase = 1
                self.break_alert.play()

    def startClock(self):
        self.work_duration = (self.work_hours.value() * 3600 +
                              self.work_minutes.value() * 60 +
                              self.work_seconds.value())
        self.break_duration = (self.break_hours.value() * 3600 +
                               self.break_minutes.value() * 60 +
                               self.break_seconds.value())
        if self.work_duration == 0 and self.break_duration == 0:
            QtWidgets.QMessageBox.information(self, "Error", "Duration can't be equal to 0")
            return
        self.phase = 1
        self.skip_button.setText("Skip\nBreak")
        self.start_button.setEnabled(False)
        self.work_hours.setEnabled(False)
        self.work_minutes.setEnabled(False)
        self.work_seconds.setEnabled(False)
        self.break_hours.setEnabled(False)
        self.break_minutes.setEnabled(False)
        self.break_seconds.setEnabled(False)
        self.skip_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.timer.start(1000)

    def skipClock(self):
        if self.phase == 1:
            hours, minutes, seconds = self.timeToHMS(self.break_duration)
            self.time_value.display(f"{hours:02}:{minutes:02}:{seconds:02}")
            self.work_duration = (self.work_hours.value() * 3600 +
                                  self.work_minutes.value() * 60 +
                                  self.work_seconds.value())
            self.phase = 2
            self.skip_button.setText("Skip\nTask")
        elif self.phase == 2:
            hours, minutes, seconds = self.timeToHMS(self.work_duration)
            self.time_value.display(f"{hours:02}:{minutes:02}:{seconds:02}")
            self.break_duration = (self.break_hours.value() * 3600 +
                                   self.break_minutes.value() * 60 +
                                   self.break_seconds.value())
            self.phase = 1
            self.skip_button.setText("Skip\nBreak")

    def stopClock(self):
        self.timer.stop()
        hours, minutes, seconds = self.timeToHMS(self.work_duration)
        self.time_value.display(f"{hours:02}:{minutes:02}:{seconds:02}")
        self.start_button.setEnabled(True)
        self.work_hours.setEnabled(True)
        self.work_minutes.setEnabled(True)
        self.work_seconds.setEnabled(True)
        self.break_hours.setEnabled(True)
        self.break_minutes.setEnabled(True)
        self.break_seconds.setEnabled(True)
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


class Settings(QtWidgets.QDialog):
    def __init__(self, parent, always_on_top, work_volume, break_volume, theme):
        super().__init__(parent)
        self.position = None
        self.always_on_top = always_on_top
        self.work_volume = work_volume
        self.break_volume = break_volume
        self.theme = theme
        self.setFixedSize(200, 300)

        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, self.always_on_top)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.central = QtWidgets.QLabel(self)
        self.central.setPixmap(self.theme)
        self.central.setFixedSize(200, 300)
        self.central.setScaledContents(True)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.always_on_top_checkbox = QtWidgets.QCheckBox("Always on top")
        self.always_on_top_checkbox.setChecked(self.always_on_top)
        self.always_on_top_checkbox.stateChanged.connect(self.changeAlwaysOnTop)
        self.layout.addWidget(self.always_on_top_checkbox)

        self.theme_label = QtWidgets.QLabel("Theme")
        self.layout.addWidget(self.theme_label)
        self.themes_combobox = QtWidgets.QComboBox()

        self.volume_label = QtWidgets.QLabel("Volume")
        self.layout.addWidget(self.volume_label)

        self.volume_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.volume_layout)

        self.work_volume_layout = QtWidgets.QVBoxLayout()
        self.volume_layout.addLayout(self.work_volume_layout)
        self.work_volume_label = QtWidgets.QLabel(f"Work: {self.work_volume}%")
        self.work_volume_layout.addWidget(self.work_volume_label)
        self.work_volume_dial = QtWidgets.QDial()
        self.work_volume_dial.setRange(0, 100)
        self.work_volume_dial.setValue(self.work_volume)
        self.work_volume_dial.setWrapping(False)
        self.work_volume_dial.setNotchesVisible(True)
        self.work_volume_dial.valueChanged.connect(self.changeWorkVolume)
        self.work_volume_layout.addWidget(self.work_volume_dial)
        self.work_volume_test_button = QtWidgets.QPushButton("Test")
        self.work_volume_test_button.clicked.connect(self.testWorkVolume)
        self.work_volume_layout.addWidget(self.work_volume_test_button)

        self.break_volume_layout = QtWidgets.QVBoxLayout()
        self.volume_layout.addLayout(self.break_volume_layout)
        self.break_volume_label = QtWidgets.QLabel(f"Break: {self.break_volume}%")
        self.break_volume_layout.addWidget(self.break_volume_label)
        self.break_volume_dial = QtWidgets.QDial()
        self.break_volume_dial.setRange(0, 100)
        self.break_volume_dial.setValue(self.break_volume)
        self.break_volume_dial.setWrapping(False)
        self.break_volume_dial.setNotchesVisible(True)
        self.break_volume_dial.valueChanged.connect(self.changeBreakVolume)
        self.break_volume_layout.addWidget(self.break_volume_dial)
        self.break_volume_test_button = QtWidgets.QPushButton("Test")
        self.break_volume_test_button.clicked.connect(self.testBreakVolume)
        self.break_volume_layout.addWidget(self.break_volume_test_button)

        self.work_alert = QtMultimedia.QSoundEffect()
        if exists(resource_path("media/sounds/alert.wav")):
            self.work_alert.setSource(QtCore.QUrl.fromLocalFile(resource_path("media/sounds/alert.wav")))
            self.work_alert.setVolume(self.work_volume / 100)

        self.break_alert = QtMultimedia.QSoundEffect()
        if exists(resource_path("media/sounds/success.wav")):
            self.break_alert.setSource(QtCore.QUrl.fromLocalFile(resource_path("media/sounds/success.wav")))
            self.break_alert.setVolume(self.break_volume / 100)

    def changeAlwaysOnTop(self):
        self.always_on_top = self.always_on_top_checkbox.isChecked()

    def changeWorkVolume(self, value):
        self.work_volume = value
        self.work_alert.setVolume(self.work_volume / 100)
        self.work_volume_label.setText(f"Work: {value}%")

    def changeBreakVolume(self, value):
        self.break_volume = value
        self.break_alert.setVolume(self.break_volume / 100)
        self.break_volume_label.setText(f"Break: {value}%")

    def testWorkVolume(self):
        self.work_alert.play()

    def testBreakVolume(self):
        self.break_alert.play()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.position is not None:
            self.move(event.globalPosition().toPoint() - self.position)

    def mouseReleaseEvent(self, event):
        self.position = None

    def settings(self):
        always_on_top = self.always_on_top_checkbox.isChecked()
        work_volume = self.work_volume
        break_volume = self.break_volume
        theme = self.theme
        return always_on_top, work_volume, break_volume, theme


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
