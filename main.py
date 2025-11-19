from typing import Any

from PyQt6 import QtGui, QtWidgets, QtCore, QtMultimedia
import sys
from pathlib import Path


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.path = Path(__file__)
        self.path_sounds = self.path.parent / "media/sounds"
        self.path_themes = self.path.parent / "media/themes"
        self.path_icon = self.path.parent / "media/icon.png"
        self.path_config = self.path.parent / "autotimer_config.ini"
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

        if (self.path_themes / f"theme_{self.theme_name}.png").exists():
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
        if (self.path_sounds / "alert.wav").exists():
            self.work_alert.setSource(QtCore.QUrl.fromLocalFile(str(self.path_sounds / "alert.wav")))
            self.work_alert.setVolume(self.work_volume / 100)

        self.break_alert = QtMultimedia.QSoundEffect()
        if (self.path_sounds / "success.wav").exists():
            self.break_alert.setSource(QtCore.QUrl.fromLocalFile(str(self.path_sounds / "success.wav")))
            self.break_alert.setVolume(self.break_volume / 100)

    def loadConfig(self) -> None:
        """Loads information on always_on_top, work_volume, break_volume and theme_name.
        If file is absent, creates one with current settings."""
        if self.path_config.exists():
            self.settings = QtCore.QSettings(str(self.path_config), QtCore.QSettings.Format.IniFormat)
            self.always_on_top = self.settings.value("app/always_on_top", type=bool)
            self.work_volume = self.settings.value("app/work_volume", type=int)
            self.break_volume = self.settings.value("app/break_volume", type=int)
            self.theme_name = self.settings.value("app/theme_name", type=str)
        else:
            self.createConfig()
        return

    def createConfig(self) -> None:
        """Creates a config file based on current settings."""
        self.path_config.touch()
        self.settings = QtCore.QSettings(str(self.path_config), QtCore.QSettings.Format.IniFormat)
        self.settings.setValue("app/always_on_top", self.always_on_top)
        self.settings.setValue("app/work_volume", self.work_volume)
        self.settings.setValue("app/break_volume", self.break_volume)
        self.settings.setValue("app/theme_name", self.theme_name)
        return

    def saveConfig(self) -> None:
        """Saves current settings to the config file."""
        self.settings.setValue("app/always_on_top", self.always_on_top)
        self.settings.setValue("app/work_volume", self.work_volume)
        self.settings.setValue("app/break_volume", self.break_volume)
        self.settings.setValue("app/theme_name", self.theme_name)
        return

    def openSettings(self) -> None:
        """Opens a modal Settings window. After the window closes, updates the config file and settings."""
        settings = Settings(self, self.always_on_top, self.work_volume, self.break_volume,
                            self.theme, self.theme_name, self.theme_names)
        settings.exec()
        self.always_on_top, self.work_volume, self.break_volume, self.theme, self.theme_name = settings.settings()
        self.saveConfig()

        if (self.path_themes / f"theme_{self.theme_name}.png").exists():
            self.theme = QtGui.QPixmap(str(self.path_themes / f"theme_{self.theme_name}.png"))
        else:
            self.theme = QtGui.QPixmap(self.window_width, self.window_height)
            self.theme.fill(QtGui.QColor("gray"))
        self.central.setPixmap(self.theme)

        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, self.always_on_top)
        self.show()

        self.work_alert.setVolume(self.work_volume / 100)
        self.break_alert.setVolume(self.break_volume / 100)
        return

    def showInfo(self) -> None:
        """Info on creator (me) and royalties."""
        try:
            with open("info.txt", "r") as file:
                info = "".join(file.readlines())
        except FileNotFoundError:
            info = ""
        QtWidgets.QMessageBox.information(self, "Info", info)
        return

    def changeOpacity(self, value) -> None:
        """Changes the window's opacity and updates the opacity label."""
        self.opacity_label.setText(f"Opacity: {value}%")
        self.setWindowOpacity(value / 100)
        return

    def changeWorkDuration(self, _) -> None:
        """Updates the work label and lcd."""
        hours = self.work_hours.value()
        minutes = self.work_minutes.value()
        seconds = self.work_seconds.value()
        self.work_label.setText(f"Work: {hours}h {minutes}m {seconds}s")
        self.time_value.display(f"{hours:02}:{minutes:02}:{seconds:02}")
        return

    def changeBreakDuration(self, _) -> None:
        """Updates the break label."""
        hours = self.break_hours.value()
        minutes = self.break_minutes.value()
        seconds = self.break_seconds.value()
        self.brake_label.setText(f"Break: {hours}h {minutes}m {seconds}s")
        return

    @staticmethod
    def timeToHMS(time: int) -> tuple[int, int, int]:
        """Translates the received time in seconds to hours, minutes and seconds."""
        hours, minutes = divmod(time, 3600)
        minutes, seconds = divmod(minutes, 60)
        return hours, minutes, seconds

    def updateTimer(self, value: int) -> int:
        """Reduces the time left by 1 second and updates the lcd."""
        value -= 1
        hours, minutes, seconds = self.timeToHMS(value)
        self.time_value.display(f"{hours:02}:{minutes:02}:{seconds:02}")
        return value

    def toggleTime(self) -> None:
        """Depending on the phase, ticks 1 second at a time.
        When the timer runs out, changes the phase and plays an alert."""
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
        return

    def startClock(self) -> None:
        """Calculates the work and break duration. If either is 0, shows a message.
        Enables what needs to be enabled, disables what needs to be disabled."""
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
        return

    def skipClock(self) -> None:
        """Skips the current phase."""
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
        return

    def stopClock(self) -> None:
        """Stops the timer, changes the time on display to work duration.
        Enables what needs to be enabled, disables what needs to be disabled."""
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
        return

    def keyPressEvent(self, event) -> None:
        """Closes the window on Escape"""
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        return

    def mousePressEvent(self, event) -> None:
        """Required to move the window with LMB."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        return

    def mouseMoveEvent(self, event) -> None:
        """Required to move the window with LMB."""
        if self.position is not None:
            self.move(event.globalPosition().toPoint() - self.position)
        return

    def mouseReleaseEvent(self, event) -> None:
        """Required to move the window with LMB."""
        self.position = None
        return


class Settings(QtWidgets.QDialog):
    def __init__(self, parent, always_on_top, work_volume, break_volume, theme, theme_name, theme_names):
        super().__init__(parent)
        self.position = None
        self.path = Path(__file__)
        self.path_sounds = self.path.parent / "media/sounds"
        self.path_themes = self.path.parent / "media/themes"
        self.always_on_top = always_on_top
        self.work_volume = work_volume
        self.break_volume = break_volume
        self.theme = theme
        self.theme_name = theme_name
        self.theme_names = theme_names
        self.window_width = 200
        self.window_height = 300
        self.setFixedSize(self.window_width, self.window_height)

        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, self.always_on_top)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.central = QtWidgets.QLabel(self)
        self.central.setPixmap(self.theme)
        self.central.setFixedSize(self.window_width, self.window_height)
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
        self.themes_combobox.addItems(self.theme_names)
        self.themes_combobox.setCurrentText(self.theme_name)
        self.themes_combobox.currentTextChanged.connect(self.changeTheme)
        self.layout.addWidget(self.themes_combobox)

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
        if (self.path_sounds / "alert.wav").exists():
            self.work_alert.setSource(QtCore.QUrl.fromLocalFile(str(self.path_sounds / "alert.wav")))
            self.work_alert.setVolume(self.work_volume / 100)

        self.break_alert = QtMultimedia.QSoundEffect()
        if (self.path_sounds / "success.wav").exists():
            self.break_alert.setSource(QtCore.QUrl.fromLocalFile(str(self.path_sounds / "success.wav")))
            self.break_alert.setVolume(self.break_volume / 100)

    def changeTheme(self, theme_name) -> None:
        """Changes the theme of the settings window. Main window updates after the settings close."""
        self.theme_name = theme_name
        if (self.path_themes / f"theme_{self.theme_name}.png").exists():
            self.theme = QtGui.QPixmap(str(self.path_themes / f"theme_{self.theme_name}.png"))
        else:
            self.theme = QtGui.QPixmap(self.window_width, self.window_height)
            self.theme.fill(QtGui.QColor("gray"))
        self.central.setPixmap(self.theme)
        return

    def changeAlwaysOnTop(self) -> None:
        """Changes always_on_top based on the check."""
        self.always_on_top = self.always_on_top_checkbox.isChecked()
        return

    def changeWorkVolume(self, value) -> None:
        """Changes the work alert volume and updates the label."""
        self.work_volume = value
        self.work_alert.setVolume(self.work_volume / 100)
        self.work_volume_label.setText(f"Work: {value}%")
        return

    def changeBreakVolume(self, value) -> None:
        """Changes the break alert volume and updates the label."""
        self.break_volume = value
        self.break_alert.setVolume(self.break_volume / 100)
        self.break_volume_label.setText(f"Break: {value}%")
        return

    def testWorkVolume(self) -> None:
        """Plays work alert to test the volume."""
        self.work_alert.play()
        return

    def testBreakVolume(self) -> None:
        """Plays break alert to test the volume."""
        self.break_alert.play()
        return

    def mousePressEvent(self, event) -> None:
        """Required to move the window with LMB."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        return

    def mouseMoveEvent(self, event) -> None:
        """Required to move the window with LMB."""
        if self.position is not None:
            self.move(event.globalPosition().toPoint() - self.position)
        return

    def mouseReleaseEvent(self, event) -> None:
        """Required to move the window with LMB."""
        self.position = None
        return

    def settings(self) -> tuple[bool, Any, Any, Any, Any]:
        """Returns the settings to the main window."""
        always_on_top = self.always_on_top_checkbox.isChecked()
        work_volume = self.work_volume
        break_volume = self.break_volume
        theme = self.theme
        theme_name = self.theme_name
        return always_on_top, work_volume, break_volume, theme, theme_name


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
