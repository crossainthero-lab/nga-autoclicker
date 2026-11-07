# NGA Auto Clicker

A desktop auto-clicker with a graphical interface and a command-line mode. It left-clicks at your current mouse position at a rate you choose. Clicking is **off** when the app starts; use the global hotkey to start or stop it.

## Install on Windows

1. Install Python 3.10 or newer. In PowerShell, you can use Windows Package Manager:

   ```powershell
   winget install --id Python.Python.3.13 -e
   ```

   Alternatively, download Python from [python.org](https://www.python.org/downloads/windows/). Include the standard Tcl/Tk component when installing. Close and reopen PowerShell after installation.

2. Download this repository from GitHub using **Code → Download ZIP**, then extract it. Alternatively, if you have Git installed, clone it:

   ```powershell
   git clone https://github.com/crossainthero-lab/nga-autoclicker.git
   ```

   If the repository is private, sign in to a GitHub account with access before cloning or downloading it.

3. Open PowerShell in the extracted `nga-autoclicker` folder and run:

   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m autoclicker
   ```

   The last command opens the app. To run it again later, open PowerShell in the same folder and repeat that last command. The commands use the virtual environment directly, so you don't need to change PowerShell's script execution policy.

The `winget` command above installs **Python**, not the auto-clicker. The auto-clicker does not currently have a published winget package.

### Using the app

Enter a **clicks per second** value and a **toggle hotkey**, then select **Apply settings**. Press the hotkey anywhere to start or stop clicking, or use the **Start / Stop** button. Closing the window stops the clicker. The initial defaults are 10 clicks per second and F8.

## Command-line mode

In the project folder, run on Windows:

```powershell
.\.venv\Scripts\python.exe -m autoclicker --cli --cps 10 --hotkey F8
.\.venv\Scripts\python.exe -m autoclicker --cli --cps 2.5 --hotkey ctrl+shift+a
.\.venv\Scripts\python.exe -m autoclicker --help
```

Press the hotkey to start or stop clicking; press **Ctrl+C** in the terminal to quit. Omit either option to use the last saved value. The rate must be greater than zero and no more than 1000 clicks per second; actual speed depends on the operating system and hardware. Settings are saved when you apply them in the UI or start CLI mode, in the user's configuration directory.

Hotkeys support single letters, function keys such as `F8`, and combinations such as `ctrl+shift+a`. `pynput` syntax such as `<ctrl>+<alt>+a` also works.

## macOS and Linux

Install Python 3.10 or newer. The GUI requires Tkinter; on Debian/Ubuntu, install it with `sudo apt install python3-tk` (use the package matching your Python installation). From the project directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m autoclicker
```

Use `.venv/bin/python -m autoclicker --cli` for terminal mode.

## Troubleshooting

- A graphical desktop session and permission to monitor keyboard input and control the mouse are required, including in CLI mode.
- On Windows, if an application running as administrator doesn't respond to clicks or the hotkey, try running the auto-clicker with the same privileges.
- On macOS, grant the terminal or Python application Accessibility and Input Monitoring permissions if prompted.
- On Linux, X11 is supported; Wayland often restricts synthetic input and global keyboard monitoring. Use an X11 session if needed.
- The app cannot control the mouse in a headless session without desktop input access.
