import os,shutil
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from resources import  icon_qrc
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
)


def get_resource_path(relative_path):
    """
    Return the absolute path of a resource.

    Works both when running the application normally
    and when the application is packaged with PyInstaller.
    """

    base_path = Path(
        getattr(
            sys,
            "_MEIPASS",
            Path(__file__).resolve().parent
        )
    )

    return str(base_path / relative_path)


class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # =========================================================
        # Load the Qt Designer interface
        # =========================================================

        try:
            ui_path = get_resource_path("resources/main.ui")
            uic.loadUi(ui_path, self)

        except Exception as error:
            QMessageBox.critical(
                self,
                "UI Error",
                f"Failed to load the application interface:\n\n{error}"
            )
            sys.exit(1)


        # =========================================================
        # Application state
        # =========================================================

        # Paths Attributes
        self.main_path_text      = ""
        self.dist_path_text      = ""
        self.build_path_text     = ""
        self.resources_path_text = ""
        self.icon_path_text      = ""
        self.output_path_text    = ""

        # Progress Related Attributes
        self.progress = 0
        self.stage = 0
        self.errorText = ""

        # Maximum progress assigned to each PyInstaller stage.
        self.dicOfStage = {
            0: 5,
            1: 10,
            2: 40,
            3: 70,
            4: 90,
            5: 100
        }

        # =========================================================
        # Configure progress bar
        # =========================================================

        self.progressBar.setValue(0)

        # =========================================================
        # Configure log table
        # =========================================================

        self.log_table.setColumnWidth(0, 105)
        self.log_table.setColumnWidth(1, 500)
        self.log_table.setColumnWidth(2, 75)

        self.cancelInstall.setEnabled(False)
        self.openFolder.setEnabled(False)

        # =========================================================
        # Connect GUI signals
        # =========================================================

        self.main_browse.clicked.connect(
            self.main_browse_func
        )

        self.dist_browse.clicked.connect(
            self.dist_browse_func
        )

        self.build_browse.clicked.connect(
            self.build_browse_func
        )

        self.resources_browse.clicked.connect(
            self.resources_browse_func
        )

        self.icon_browse.clicked.connect(
            self.icon_browse_func
        )

        self.install.clicked.connect(
            self.install_func
        )
        self.cancelInstall.clicked.connect(
            self.cancel_build
        )
        self.openFolder.clicked.connect(
            self.open_output_folder
        )


        # =========================================================
        # Create PyInstaller process
        # =========================================================

        self.processInstall = QProcess(self)

        # Combine stdout and stderr into one stream.
        self.processInstall.setProcessChannelMode(
            QProcess.MergedChannels
        )

        # Receive PyInstaller output while it is running.
        self.processInstall.readyReadStandardOutput.connect(
            self.printstd
        )

        # Called when PyInstaller finishes.
        self.processInstall.finished.connect(
            self.process_finished
        )

        pyinstaller_path = shutil.which("pyinstaller")

        if pyinstaller_path is None:
            QMessageBox.critical(
                self,
                "PyInstaller Not Found",
                "PyInstaller could not be found.\n\n"
                "Please install PyInstaller and make sure it is "
                "available in your system PATH."
            )
            self.install.setEnabled(False)
        else:
            print("PyInstaller found:")
            print(pyinstaller_path)






    # =============================================================
    # Browse Functions
    # =============================================================

    def main_browse_func(self):
        """Select the Python entry-point file."""

        main_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select main.py",
            ".",
            "Python Files (*.py)"
        )

        if not main_path:
            return

        print("Python Entry Point:\n", main_path)

        self.main_path.setText(main_path)
        self.main_path_text = main_path

        QMessageBox.information(
            self,
            "Notification",
            "main.py was successfully selected."
        )

    def dist_browse_func(self):
        """Select the PyInstaller distribution directory."""

        dist_path = QFileDialog.getExistingDirectory(
            self,
            "Select dist directory",
            "."
        )

        if not dist_path:
            return

        print("Distribution Directory:\n", dist_path)

        self.dist_path.setText(dist_path)
        self.dist_path_text = dist_path

        QMessageBox.information(
            self,
            "Notification",
            "Distribution directory was successfully selected."
        )

    def build_browse_func(self):
        """Select the PyInstaller build directory."""

        build_path = QFileDialog.getExistingDirectory(
            self,
            "Select build directory",
            "."
        )

        if not build_path:
            return

        print("Build Directory:\n", build_path)

        self.build_path.setText(build_path)
        self.build_path_text = build_path

        QMessageBox.information(
            self,
            "Notification",
            "Build directory was successfully selected."
        )

    def resources_browse_func(self):
        """Select the application resources directory."""

        resources_path = QFileDialog.getExistingDirectory(
            self,
            "Select resources directory",
            "."
        )

        if not resources_path:
            return

        print("Resources:\n", resources_path)

        self.resources_path.setText(resources_path)
        self.resources_path_text = resources_path

        QMessageBox.information(
            self,
            "Notification",
            "Resources directory was successfully selected."
        )

    def icon_browse_func(self):
        (icon_path,_) = QFileDialog.getOpenFileName(self,"Select Image :",
                                     ".",
                                     "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.ico *.svg)")
        if not icon_path:
            return

        print("Icon Path:\n", icon_path)

        self.icon_path_editLine.setText(icon_path)
        self.icon_path_text = icon_path

        QMessageBox.information(
            self,
            "Notification",
            "Icon File was successfully selected."
        )


    # =============================================================
    # Build Confirmation
    # =============================================================

    def install_func(self):
        """Validate the configuration and start the build."""

        # Reset build state.
        self.progress = 0
        self.stage = 0
        self.errorText = ""
        self.cancel_requested = False

        self.progressBar.setValue(0)

        # Remove previous log messages.
        self.log_table.setRowCount(0)

        # ---------------------------------------------------------
        # Validate selected paths
        # ---------------------------------------------------------

        errors = []

        if not Path(self.main_path_text).is_file():
            errors.append(
                "Python Entry Point is missing or invalid."
            )

        if not Path(self.dist_path_text).is_dir():
            errors.append(
                "Distribution Directory is missing or invalid."
            )

        if not Path(self.build_path_text).is_dir():
            errors.append(
                "Build Directory is missing or invalid."
            )

        if not Path(self.resources_path_text).is_dir():
            errors.append(
                "Resources Directory is missing or invalid."
            )

        # ---------------------------------------------------------
        # Stop if configuration is invalid
        # ---------------------------------------------------------

        if errors:

            QMessageBox.warning(
                self,
                "Invalid Configuration",
                "Please correct the following:\n\n"
                + "\n".join(
                    f"• {error}"
                    for error in errors
                )
            )

            return

        # ---------------------------------------------------------
        # Display configuration for confirmation
        # ---------------------------------------------------------

        details = (
            f"Python Entry Point:\n"
            f"{self.main_path_text}\n\n"

            f"Distribution Directory:\n"
            f"{self.dist_path_text}\n\n"

            f"Build Directory:\n"
            f"{self.build_path_text}\n\n"

            f"Resources Directory:\n"
            f"{self.resources_path_text}"
            "\n"
            f"Console Mode : {( 'Console       (Default)' if self.console.isChecked() else 'Windowed')} \n"
            f"Output Type    : {( 'One Directory (Default)' if self.one_dir.isChecked() else 'One File')}\n"
            f"Application Name : {(self.name_text.text() if self.name_text.text() != '' else 'main')}\n"
            f"Icon Path       : {(self.icon_path_text if self.icon_path_text != '' else 'None (Default)')}"
        )

        result = QMessageBox.question(
            self,
            "Confirm Build",
            f"Are you sure you want to start the build?\n\n"
            f"{details}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result != QMessageBox.Yes:
            print("Build cancelled.")
            return

        print("Installing...")

        self.installing()

    def cancel_build(self):
        if self.processInstall.state() == QProcess.NotRunning:
            return

        self.cancel_requested = True
        self.processInstall.kill()
        self.cancelInstall.setEnabled(False)


    def open_output_folder(self):
        path = os.path.abspath(self.output_path_text)

        if platform.system() == "Windows":
            subprocess.Popen(f'explorer "{path}"')
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux / Unix
            subprocess.Popen(["xdg-open", path])

        QMessageBox.information(self,
                                "Open Folder Location",
                                f"Folder Opened Successfully at \n{self.output_path_text}")


    # =============================================================
    # Start PyInstaller
    # =============================================================

    def installing(self):
        """Create the PyInstaller command and execute it."""

        # ---------------------------------------------------------
        # Make sure another build isn't already running.
        # ---------------------------------------------------------

        if self.processInstall.state() != QProcess.NotRunning:

            QMessageBox.warning(
                self,
                "Build In Progress",
                "A PyInstaller build is already running."
            )

            return

        # ---------------------------------------------------------
        # Construct PyInstaller arguments.
        # ---------------------------------------------------------

        arguments = [
            "-y","--clean",

            self.main_path_text,
        ]
        if os.path.exists(self.dist_path_text):
            print("Yes")
            arguments.append("--distpath")
            arguments.append(self.dist_path_text)
        else:
            print("No")

        if os.path.exists(self.build_path_text):
            print("Yes")
            arguments.append("--workpath")
            arguments.append(self.build_path_text)
        else:
            print("No")

        if os.path.exists(self.resources_path_text):
            print("Yes")
            arguments.append("--add-data")
            arguments.append(f"{self.resources_path_text}:resources")
        else:
            print("No")

        if self.windowed.isChecked():
            arguments.append("-w")
        else:
            arguments.append("-c")

        if self.one_dir.isChecked():
            arguments.append("-D")
        else:
            arguments.append("-F")

        if self.name_text.text() != "":
            arguments.append("-n")
            arguments.append(self.name_text.text())
        else:
            arguments.append("-n")
            arguments.append("main")

        if Path(self.icon_path_text).is_file() :
            arguments.append("--icon")
            arguments.append(self.icon_path_text)
        else:
            pass
        # ---------------------------------------------------------
        # Print arguments for debugging.
        # ---------------------------------------------------------

        print("\nPyInstaller arguments:")

        for argument in arguments:
            print(repr(argument))

        # ---------------------------------------------------------
        # Disable build button while process is running.
        # ---------------------------------------------------------

        self.install.setEnabled(False)
        self.openFolder.setEnabled(False)
        self.cancelInstall.setEnabled(True)

        # ---------------------------------------------------------
        # Start PyInstaller asynchronously.
        # ---------------------------------------------------------

        self.processInstall.start(
            "pyinstaller",
            arguments
        )

    # =============================================================
    # Read PyInstaller Output
    # =============================================================

    def printstd(self):
        """
        Read all currently available PyInstaller output.

        Because stdout and stderr are merged, this function
        receives both normal output and errors.
        """

        output = self.processInstall.readAllStandardOutput()

        text = bytes(output).decode(
            "UTF-8",
            errors="replace"
        )

        if not text:
            return

        # Print the raw output to the console.
        print(text, end="")

        # PyInstaller may send multiple lines at once.
        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            self.process_log_line(line)

    # =============================================================
    # Process Individual Log Line
    # =============================================================

    def process_log_line(self, text):
        """Process one PyInstaller log line."""

        # Display the message in the log table.
        self.log_table_displayFunction(text)

        # ---------------------------------------------------------
        # Save errors for the error dialog.
        # ---------------------------------------------------------

        if "ERROR" in text.upper():

            self.errorText += text + "\n"

        # ---------------------------------------------------------
        # Detect PyInstaller stages.
        # ---------------------------------------------------------

        if (
            "checking Analysis" in text
            and self.stage == 0
        ):

            self.stage = 1
            self.progress = 5

        elif (
            "Running Analysis" in text
            and self.stage == 1
        ):

            self.stage = 2
            self.progress = 10

        elif (
            "Processing standard module" in text
            and self.stage == 2
        ):

            self.stage = 3
            self.progress = 40

        elif (
            "Building PKG" in text
            and self.stage == 3
        ):

            self.stage = 4
            self.progress = 70

        elif (
            "Building EXE" in text
            and self.stage == 4
        ):

            self.stage = 5
            self.progress = 90

        # Update progress bar.
        self.progressBar.setValue(
            self.progress
        )

    # =============================================================
    # Log Table
    # =============================================================

    def log_table_displayFunction(self, text):
        """Add one log message to the log table."""

        # ---------------------------------------------------------
        # Extract log type and message.
        #
        # Example:
        #
        # "123 INFO: Building EXE"
        #
        # becomes:
        #
        # type    = INFO
        # message = Building EXE
        # ---------------------------------------------------------

        parts = text.split(":", 1)

        log_type = "UNKNOWN"
        log_message = text

        if len(parts) == 2:

            header_parts = parts[0].strip().split()

            if len(header_parts) >= 2:
                log_type = header_parts[1]

            log_message = parts[1].strip()

        # ---------------------------------------------------------
        # Define colors for different log types.
        # ---------------------------------------------------------

        color_map = {
            "INFO": (
                QColor("green"),
                QColor("white")
            ),

            "WARNING": (
                QColor("yellow"),
                QColor("black")
            ),

            "ERROR": (
                QColor("red"),
                QColor("white")
            ),

            "FINISH": (
                QColor("darkBlue"),
                QColor("white")
            )
        }

        background, foreground = color_map.get(
            log_type,
            (
                QColor("white"),
                QColor("black")
            )
        )

        # ---------------------------------------------------------
        # Create table items.
        # ---------------------------------------------------------

        time_item = QTableWidgetItem(
            datetime.now().strftime("%H:%M:%S")
        )

        message_item = QTableWidgetItem(
            log_message
        )

        type_item = QTableWidgetItem(
            log_type
        )

        # ---------------------------------------------------------
        # Apply colors.
        # ---------------------------------------------------------

        for item in (
            time_item,
            message_item,
            type_item
        ):
            item.setBackground(background)
            item.setForeground(foreground)

        # ---------------------------------------------------------
        # Add row to the bottom of the table.
        # ---------------------------------------------------------

        row = self.log_table.rowCount()

        self.log_table.insertRow(row)

        self.log_table.setItem(
            row,
            0,
            time_item
        )

        self.log_table.setItem(
            row,
            1,
            message_item
        )

        self.log_table.setItem(
            row,
            2,
            type_item
        )

        # Keep the newest message visible.
        self.log_table.scrollToBottom()

        if "Build complete!" in log_message:
            parts = log_message.split("in:", 1)

            if len(parts) == 2:
                self.output_path_text = parts[1].strip()

    # =============================================================
    # Process Finished
    # =============================================================

    def process_finished(self, exit_code, exit_status):
        """Handle the result of the PyInstaller process."""

        # Re-enable the build button.
        self.install.setEnabled(True)
        self.cancelInstall.setEnabled(False)


        # ---------------------------------------------------------
        # Successful build
        # ---------------------------------------------------------

        if (
            exit_status == QProcess.NormalExit
            and exit_code == 0
        ):

            self.progress = 100

            self.progressBar.setValue(
                self.progress
            )

            self.log_table_displayFunction(
                "00 FINISH: Build completed successfully."
            )

            QMessageBox.information(
                self,
                "Build Complete",
                "PyInstaller finished successfully."

            )
            self.openFolder.setEnabled(True)


        # ---------------------------------------------------------
        # Failed build
        # ---------------------------------------------------------
        elif self.cancel_requested == True:
            self.log_table_displayFunction(
                "00 FINISH: Build cancelled by user."
            )

            self.progressBar.setValue(0)

            print("Build cancelled by user.")
            QMessageBox.warning(
                self,
                "Build cancelled",
                "Build cancelled by user"
            )

            return
        else:

            self.log_table_displayFunction(
                f"00 FINISH: Build failed "
                f"with exit code ({exit_code})."
            )

            error_message = self.errorText.strip()

            if not error_message:
                error_message = (
                    "PyInstaller terminated unexpectedly."
                )

            QMessageBox.critical(
                self,
                "Build Failed",
                error_message
            )

        print("\nProcess finished.")
        print("Exit code:", exit_code)
        print("Exit status:", exit_status)


# =============================================================
# Application Entry Point
# =============================================================

def main():

    app = QtWidgets.QApplication(sys.argv)

    window = Ui()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()