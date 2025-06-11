import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import datetime
from plyer import notification  # For desktop notifications

# Define network locations and their IPs
networks = {
    "District": "10.11.0.1",
    "CO": "10.80.0.1",
    "Tech Dept": "10.20.0.1",
    "High School": "10.50.0.1",
    "Middle School": "10.191.0.1",
    "Hartwell Elementary": "10.150.0.1",
    "North Hart": "10.102.0.1",
    "South Hart": "10.202.0.1",
    "Bus Shop": "10.195.0.1",
    "Maintenance Dept": "10.23.0.1",
    "Ag Center": "10.32.0.1",
    "Field House": "10.70.0.1",
    "Google": "8.8.8.8",
}

# Previous status storage
prev_status = {name: None for name in networks}

# Initialize the window
window = tk.Tk()
window.title("Network Status Monitor")
window.geometry("200x450")  # Adjust size as needed

# Styling
style = ttk.Style(window)
style.configure("TLabel", font=('Helvetica', 10))
style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))
style.configure("Online.TLabel", background="green")
style.configure("Offline.TLabel", background="red")

# Status Labels Mapping
status_labels = {}

# Logging Function
def log_status(name, ip, online):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Online" if online else "Offline"
    log_entry = f"{timestamp} - {name} ({ip}): {status}\n"
    with open("network_status.log", "a") as log_file:
        log_file.write(log_entry)

# Ping Function
def ping_address(ip_address):
    response = subprocess.run(["ping", "-n", "1", ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return response.returncode == 0

# Notification Function
def notify_status_change(name, online):
    notification.notify(
        title="Network Status Change",
        message=f"{name} is now {'online' if online else 'offline'}.",
        app_name="Network Status Monitor"
    )

# Update Status Function
def update_status():
    for name, ip in networks.items():
        online = ping_address(ip)
        # Log the status
        log_status(name, ip, online)
        # Update GUI
        status_labels[name].config(text="Online" if online else "Offline",
                                   style="Online.TLabel" if online else "Offline.TLabel")
        # Check for status change to trigger notification
        if prev_status[name] is not None and prev_status[name] != online:
            notify_status_change(name, online)
        prev_status[name] = online  # Update previous status

    window.after(10000, update_status)  # Schedule next update

# GUI Layout
header = ttk.Label(window, text="Network Status Monitor", style="Header.TLabel")
header.pack(pady=10)

# Network Status Section
for name in networks.keys():
    frame = ttk.Frame(window)
    ttk.Label(frame, text=name+":", font=('Helvetica', 10)).pack(side=tk.LEFT)
    status_label = ttk.Label(frame, text="Checking...", font=('Helvetica', 10))
    status_label.pack(side=tk.RIGHT)
    frame.pack(pady=2)
    status_labels[name] = status_label

# Manual Update Button
update_button = ttk.Button(window, text="Update Now", command=update_status)
update_button.pack(pady=20)

# Start the periodic update in a separate thread
threading.Thread(target=update_status, daemon=True).start()

window.mainloop()
