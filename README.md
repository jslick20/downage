# Network Status Monitor

A simple desktop application built with Tkinter to monitor network connectivity for a list of predefined hosts. Periodically pings each host, logs status changes, and provides desktop notifications on state changes.

## Features

* Periodic ping checks (every 10 seconds by default)
* Manual "Update Now" button
* Color-coded status labels (green for online, red for offline)
* Desktop notifications on status change via Plyer
* Status logging to `network_status.log`
* Simple configuration of hosts in the source code

## Requirements

* Python 3.x
* **Plyer** (for desktop notifications)
* Tkinter (bundled with most Python installations)

## Installation

1. **Clone or download** this repository.

2. **Create and activate** a virtual environment (recommended):

   ```bash
   python -m venv .venv
   # On Windows
   .\.venv\Scripts\activate
   # On macOS / Linux
   source .venv/bin/activate
   ```

3. **Install** the Python dependency:

   ```bash
   pip install plyer
   ```

4. *(Linux only)* If Tkinter is not available, install with your package manager:

   ```bash
   sudo apt install python3-tk    # Debian/Ubuntu
   sudo dnf install python3-tkinter  # Fedora
   ```

## Usage

1. **Open** the script in your terminal:

   ```bash
   python network_status_monitor.py
   ```

2. The GUI will launch, showing each host and its current status.

3. Click **Update Now** to manually trigger an immediate ping round.

4. The app will automatically re-check every 10 seconds.

5. Status logs are appended to `network_status.log` in the same directory.

## Configuration

* Hosts to monitor are defined in the `networks` dictionary at the top of the script.
* Modify the dictionary entries (`"Name": "IP_ADDRESS"`) to add or remove hosts.
* Change the update interval by editing the `window.after(10000, update_status)` delay (value in milliseconds).

## Logging

All status checks are logged with timestamps to `network_status.log`. Example entry:

```
2025-06-11 15:30:05 - District (10.11.0.1): Online
```

## Troubleshooting

* **No notifications**: Ensure your OS allows plyer notifications; on some Linux desktop environments you may need a notification daemon.
* **Tkinter errors**: If you see `ModuleNotFoundError: No module named 'tkinter'`, install the OS package for Tkinter as noted above.

## Contributing

Feel free to fork the project and open pull requests. Improvements could include:

* Dynamic host list UI
* CSV or JSON configuration loading
* Parallel ping performance enhancements
* Cross-platform packaging (e.g. PyInstaller)

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.
