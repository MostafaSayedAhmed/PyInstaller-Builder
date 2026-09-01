# PyInstaller GUI

A desktop graphical interface for **PyInstaller** that simplifies the process of converting Python applications into standalone executable applications.
Instead of repeatedly typing PyInstaller commands in a terminal, this application provides a user-friendly **PyQt5 GUI** where you can configure the build, select required directories and resources, monitor the build process in real time, and access the generated output.

---

## 📌 Overview

**PyInstaller GUI** is a Python/PyQt5 desktop application designed to make PyInstaller easier to use, especially for users who frequently package Python applications.

The application acts as a graphical frontend for the PyInstaller command-line tool.

It allows the user to configure:

- Python entry-point file (.py)
- Distribution directory
- Build/work directory
- Resources directory
- Application icon
- Application name
- Console/windowed mode
- One-file/one-directory output

After configuration, the application launches PyInstaller as an external process using Qt's `QProcess`.

The PyInstaller output is captured in real time and displayed inside the application's log interface.
<img width="500" height="544" alt="image" src="https://github.com/user-attachments/assets/9daefd49-4ba4-42ce-9417-b7da9fd2e53e" />

---

## ✨ Features

### 🐍 Python Entry Point

Select the Python file that will be used as the application's entry point.

Example:

```text
main.py
```
The application verifies that the selected file exists before starting the build.

### 📦 Distribution Directory

Select the directory where PyInstaller will place the generated application.

Equivalent PyInstaller option:

```bash
--distpath <directory>
```

### 🔨 Build Directory

Select the directory used by PyInstaller for temporary build files.

Equivalent PyInstaller option:
```bash
--workpath <directory>
```

### 📁 Resource Support

Select a resources directory and automatically include it in the generated application.

The application generates:

```bash
--add-data "<resources>:resources"
```

This allows applications containing resources such as:

```Plaintext
resources/
├── main.ui
├── icons/
├── images/
└── other files
```

to package those resources with the executable.

### 🎨 Application Icon

Select an application icon that will be passed to PyInstaller.

Equivalent option:

```bash
--icon <icon>
```

Supported image formats include:

- PNG
- JPG
- JPEG
- BMP
- GIF
- SVG
- ICO

For Windows executable icons, PyInstaller may require an appropriate .ico file depending on the target configuration.

### 🖥️ Console / Windowed Mode

The GUI provides a choice between:

Console mode

```bash
-c
```

and:

Windowed mode

```bash
-w
```

Windowed mode is useful for GUI applications where a terminal window should not appear when the application starts.

📦 One-Directory / One-File Builds

The application supports both PyInstaller output modes.

One Directory

```bash
-D
```

Produces an application directory containing the executable and its dependencies.

Example:
```Plaintext
dist/
└── MyApplication/
    ├── MyApplication.exe
    ├── Python libraries
    └── application resources
```

One File
```bash
-F
```

Produces a single executable.

Example:
```Plaintext
dist/
└── MyApplication.exe
```

### 📊 Real-Time Build Monitoring

One of the main features of this project is real-time PyInstaller output monitoring.

Instead of using:

```Python
subprocess.run(...)
```
the application uses Qt's:
```Python
QProcess
```
This allows PyInstaller to run asynchronously without blocking the Qt event loop.

The GUI remains responsive while PyInstaller is running.

The application captures PyInstaller's output using:

readyReadStandardOutput

and displays the output in the application's log table.

### 📝 Build Log

The application provides a dedicated log table containing:

| Time	   | Message                         |	Type   |
|----------|---------------------------------|---------|
| 12:30:01 |	Checking Analysis            |	INFO   |
| 12:30:02 |	Running Analysis             |	INFO   |
| 12:30:05 |	Processing standard module   |	INFO   |
| 12:30:10 |	Building PKG                 |	INFO   |
| 12:30:15 |	Building EXE                 |	INFO   |
| 12:30:20 |	Build completed successfully |	FINISH |

The log system also distinguishes between:

- INFO
- WARNING
- ERROR
- FINISH
- UNKNOWN

This makes long PyInstaller builds easier to understand and monitor.

### 📈 Build Progress

The application provides a graphical progress bar representing the approximate progress of the PyInstaller build.

PyInstaller does not expose a simple universal percentage-complete API, so the application estimates progress by detecting important PyInstaller stages.

The current stages include:

```Plaintext

Start
  │
  ├── Checking Analysis        → ~5%
  │
  ├── Running Analysis         → ~10%
  │
  ├── Processing Modules       → ~40%
  │
  ├── Building PKG             → ~70%
  │
  ├── Building EXE             → ~90%
  │
  └── Build Complete           → 100%
```

The progress indicator should therefore be considered an estimated build progress, rather than an exact measurement.

### ❌ Build Cancellation

The user can cancel an active PyInstaller build.

The application terminates the running QProcess and reports:

Build cancelled by user.

The GUI then returns to its normal state and allows another build to be started.

### 📂 Open Output Folder

After a successful build, the application allows the user to open the generated output directory directly.

The application detects the operating system and uses the appropriate command:

- Windows
- explorer
- macOS
- open
- Linux
- xdg-open

This provides a platform-aware way of accessing the generated application.

### 🏗️ Project Architecture

The project is intentionally designed around a relatively simple architecture.

```Plaintext

User
 │
 ▼
PyQt5 GUI
 │
 ├── Configuration
 │
 ├── File Selection
 │
 ├── Build Options
 │
 └── Build Confirmation
 │
 ▼
QProcess
 │
 ▼
PyInstaller
 │
 ├── stdout
 └── stderr
 │
 ▼
Log Processing
 │
 ├── Log Table
 │
 ├── Error Detection
 │
 └── Build Stage Detection
 │
 ▼
Progress / Build Result
```

### 🛠️ Technologies Used
Python

The application is written in Python.

Python is responsible for:

- Application logic
- File validation
- Path management
- Process configuration
- Build argument generation
- Output processing
- Platform detection
- PyQt5

The graphical interface is implemented using PyQt5.

Important components include:

- QMainWindow
- QMessageBox
- QFileDialog
- QTableWidget
- QTableWidgetItem
- QProcess
- Qt Designer

The graphical interface is designed using Qt Designer.

The UI is stored separately as:

```bash
resources/main.ui
```

The interface is loaded at runtime using:

```python
uic.loadUi()
```

This keeps the GUI design separated from the Python application logic.

PyInstaller

PyInstaller performs the actual Python application packaging.

The GUI does not implement its own Python packaging system.

Instead, it acts as a graphical frontend that constructs and executes PyInstaller commands.

For example, the GUI can generate an equivalent command such as:

```bash
pyinstaller -y --clean main.py \
    --distpath ./dist \
    --workpath ./build \
    --add-data "./resources:resources" \
    -w \
    -D \
    -n MyApplication \
    --icon application.ico
```
    
### 📁 Project Structure

The repository is organized approximately as follows:

```Plaintext
PyInstaller-GUI/
│
├── main.py
│
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
│
├── resources/
│   ├── main.ui
│   └── icon_qrc.py
│
├── dist/
│   └── ...
│
├── build/
│   └── ...
│
├── installer/
│   └── ...
│
└── screenshots/
    └── ...
```

dist/, build/, and generated installer files may be excluded from version control depending on the project's release strategy.

### ⚙️ Requirements

The project requires:

- Python 3.x
- PyQt5
- PyInstaller

Install the Python dependencies using:

```bash
pip install -r requirements.txt
```

A typical requirements.txt contains:

- PyQt5
- PyInstaller

### 🚀 Running the Application

Clone the repository:

```bash
git clone <repository-url>
```

Enter the project directory:

```bash
cd PyInstaller-GUI
```

Create a virtual environment:

```bash
python -m venv venv
```
Activate it on Windows:

```bash
venv\Scripts\activate
```
Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

### 🖥️ Using the Application

#### Step 1 — Select Python Entry Point

Click:

Browse

and select the Python file that should be packaged.

For example:

```bash
C:\Projects\MyApplication\main.py
```

#### Step 2 — Select Distribution Directory

Select the directory where the final PyInstaller output should be generated.

Example:

```bash
C:\Projects\MyApplication\dist
```

#### Step 3 — Select Build Directory

Select the working directory used during the PyInstaller build.

Example:

```bash
C:\Projects\MyApplication\build
```

#### Step 4 — Select Resources

Select the application's resources directory.

For example:

```Plaintext
resources/
├── main.ui
├── images/
└── icons/
```

The GUI automatically passes this directory to PyInstaller using:

```bash
--add-data
```

#### Step 5 — Select Application Icon

Optionally select an application icon.

Example:

```bash
resources/application.ico
```

#### Step 6 — Configure Build Options

Choose:

Console Mode

or:

Windowed Mode

Then select:

One Directory

or:

One File

You can also specify the generated application's name.

For example:

MyApplication

#### Step 7 — Start Build

Click the build/install button.

The application validates the selected configuration before starting PyInstaller.

A confirmation dialog displays the selected settings.

After confirmation, PyInstaller starts asynchronously.

#### Step 8 — Monitor the Build

The log table displays PyInstaller's output while the process is running.

The progress bar provides an estimated indication of build progress.

#### Step 9 — Build Completion

After PyInstaller exits successfully:

Build completed successfully.

The application:

1. Sets progress to 100%
2. Displays the final build message
3. Enables the output-folder button
4. Allows the user to open the generated directory

### 🔄 QProcess Workflow

The application uses QProcess instead of blocking subprocess calls.

The basic workflow is:

```Python
self.processInstall = QProcess(self)

self.processInstall.setProcessChannelMode(
    QProcess.MergedChannels
)

self.processInstall.readyReadStandardOutput.connect(
    self.printstd
)

self.processInstall.finished.connect(
    self.process_finished
)

self.processInstall.start(
    "pyinstaller",
    arguments
)
```

This is important because a GUI application must not block the Qt event loop during a long-running operation.

A blocking approach such as:

```Python
subprocess.run(...)
```

would prevent the GUI from processing events until PyInstaller finishes.

Using QProcess allows:

```Plaintext
GUI
 │
 ├─────────────── remains responsive
 │
 ▼
QProcess
 │
 ▼
PyInstaller
```

### 🔐 Input Validation

Before starting the build, the application validates the required paths.

The following must exist:

- Python Entry Point
- Distribution Directory
- Build Directory
- Resources Directory

If any required path is invalid, the build is not started.

Example:

Invalid Configuration

Please correct the following:

• Python Entry Point is missing or invalid.
• Distribution Directory is missing or invalid.

This prevents many avoidable PyInstaller errors.

### 🧹 Clean Builds

The application uses:

```bash
-y
```

and:

```bash
--clean
```

The -y option automatically confirms replacement of existing output where applicable.

The --clean option removes PyInstaller's temporary cache before building.

This helps produce cleaner and more predictable builds.

### ⚠️ Important Limitations

This project is intentionally a PyInstaller GUI frontend, not a replacement for PyInstaller.

The current version has several limitations.

Estimated Progress

The progress bar is based on detected PyInstaller stages rather than exact build percentage.

Therefore:

90%

does not necessarily mean exactly 90% of the build work has completed.

PyInstaller Output Changes

The application detects certain messages such as:

- Checking Analysis
- Running Analysis
- Building PKG
- Building EXE

If PyInstaller changes its output format in a future release, some progress-stage detection may need to be updated.

Python / PyInstaller Availability

PyInstaller must be installed and accessible from the environment used to run the application.

For example:

```bash
pyinstaller --version
```

should return a valid version.

Platform-Specific Builds

PyInstaller generally creates executables for the platform on which it is executed.

For example:

Windows → Windows executable
Linux   → Linux executable
macOS   → macOS application

A Windows .exe generated on Windows should not be expected to run natively on Linux.

Separate builds should therefore be produced for different target platforms.

### 🧪 Testing

Before releasing the application, the following cases should be tested.

|             Test                  |	Expected Result                          |
|-----------------------------------|--------------------------------------------| 
| Valid Python file	                |  Build starts                              |
| Missing Python file	            |  Warning displayed                         |
| Invalid distribution directory    |  Build prevented                           |
| Invalid build directory	        |  Build prevented                           |
| Invalid resources directory	    |  Build prevented                           |
| No icon selected	                |  Build proceeds using default icon         |
| Custom icon selected	            |  Icon passed to PyInstaller                | 
| One-file mode	                    |  Single executable generated               |
| One-directory mode	            |  Application directory generated           | 
| Console mode	                    |  Console-enabled executable generated      | 
| Windowed mode	                    |  GUI executable generated                  |
| Successful build	                |  Progress reaches 100%                     |
| PyInstaller error	                |  Error dialog displayed                    |
| Cancel during build	            |  Process terminated                        |
| Start second build while running  |	 Build prevented                         | 
| Open output folder	            |  Output directory opened                   | 

### 🐛 Error Handling

The application attempts to handle common errors through GUI dialogs.

Examples include:

- UI loading failure
- Invalid configuration
- PyInstaller build failure
- Build cancellation
- Unexpected process termination

Errors generated by PyInstaller are captured and displayed to the user.

### 🎯 Project Goals

The main goals of this project are:

- Provide a simple graphical interface for PyInstaller.
- Remove the need to manually construct long PyInstaller commands.
- Make common packaging options easily accessible.
- Provide real-time build logs.
- Keep the GUI responsive during long builds.
- Provide visual feedback through a progress bar.
- Make the packaging workflow easier for users who are less comfortable with command-line tools.

### 🧠 What I Learned

This project provided practical experience with several important software-development concepts.

- Python
- File and directory handling
- pathlib
- Operating-system interaction
- Exception handling
- Process execution
- Application state management
- PyQt5
- Signals and slots
- QProcess
- QFileDialog
- QMessageBox
- QTableWidget
- GUI state management
- Asynchronous process handling
- Software Development
- Separating GUI and application logic
- Input validation
- Error handling
- User confirmation workflows
- Long-running process management
- Cross-platform considerations
- Application packaging
- Release preparation

### 🔮 Future Improvements

The current version focuses on the core PyInstaller workflow.

Possible future versions could introduce:

- .spec file support
- Custom PyInstaller command options
- Hidden-import management
- Multiple --add-data entries
- Multiple --add-binary entries
- Recursive resource selection
- Environment/interpreter selection
- Python virtual-environment detection
- PyInstaller version detection
- Build history
- Saved build profiles
- Configuration files
- Dark/light themes
- Better progress estimation
- Build presets
- Drag-and-drop file selection
- Custom output naming
- Advanced PyInstaller options
- Automatic dependency detection
- Build logs exported to files

These features can be added gradually without changing the core concept of the application.

### 📌 Version

Current development version:

v1.0.0

The first version focuses on the essential PyInstaller packaging workflow rather than exposing every PyInstaller option.

### 📜 License

This project is distributed under the terms of the license included in:

LICENSE
👨‍💻 Author

Mostafa Sayed

Software Application Development & Automation

This project was developed as part of a practical portfolio focused on:

- Python
- Desktop Application Development
- PyQt5
- Automation
- Software Packaging
- Application Deployment

### ⭐ Contributing

Contributions, suggestions, and improvements are welcome.

If you find a bug or have an idea for improving the application:

Open an issue.
Describe the problem or proposed improvement.
Provide reproduction steps where applicable.
Submit a pull request if you would like to implement the change.

### 📷 Screenshots

Screenshots of the application are placed inside:

screenshots/

For example:
```Plaintext
screenshots/
├── main-interface.png
├── Confirm-Build.png
├── Build-Process.png
└── Build-Complete.png

```

### 📚 References
- [PyInstaller Documentation](https://pyinstaller.org)
- [PyQt5 Documentation](https://riverbankcomputing.com)
- [Qt QProcess Documentation](https://qt.io)
- [Python Documentation](https://python.org)
- [Qt Designer Documentation](https://qt.io)
