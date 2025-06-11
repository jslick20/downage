import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from tkinter import Toplevel, Text, BooleanVar, StringVar
from tkcalendar import Calendar, DateEntry
import subprocess
import threading
import datetime
import os
import re
from plyer import notification
from tkinter import PhotoImage
from PIL import Image, ImageTk


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
window.geometry("250x390")  # Adjust size as needed
gear_icon = PhotoImage(file="assets/gear.png")

window.attributes('-topmost', True)

# Styling
style = ttk.Style(window)
style.configure("TLabel", font=('Helvetica', 10))
style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))
style.configure("Online.TLabel", background="green")
style.configure("Offline.TLabel", background="red")

# Status Labels Mapping
status_labels = {}

# Define Ping Settings Variables at the global scope
echo_request_var = tk.StringVar(value='1')  # Number of Echo Requests
timeout_var = tk.StringVar(value='1')  # Timeout in Seconds

# Ping Settings Variables
#echo_request_var = tk.StringVar(value='1')  # Number of Echo Requests
#timeout_var = tk.StringVar(value='1')  # Timeout in Seconds

# Update Interval Variable (in seconds)
update_interval_var = tk.StringVar(value='30')  # Default to 30 seconds

# Logging Function
def log_status(name, ip, result):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Online" if result["online"] else "Offline"
    additional_info = f"Success Rate: {result['success_rate']}%, Attempts: {result['attempts']}"

    if result["online"]:
        additional_info += f", Average Latency: {result['average_latency']}ms, Min Latency: {result['min_latency']}ms, Max Latency: {result['max_latency']}ms"
    else:
        additional_info += f", Error: {result['error_message']}"

    log_entry = f"{timestamp} - {name} ({ip}): {status}. {additional_info}\n"
    with open("network_status.log", "a") as log_file:
        log_file.write(log_entry)


# Function to view log
def export_log():
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        initialfile=f"network_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    )
    if filename:  # Check if a filename was selected
        with open(filename, "w") as file:
            with open("network_status.log", "r") as log_file:
                file.write(log_file.read())
        notification.notify(
            title="Log Exported",
            message=f"Log has been exported as {filename}",
            app_name="Network Status Monitor"
        )

# Adjust the view_log function to include an Export button
def view_log():
    log_window = tk.Toplevel(window)
    log_window.title("Network Log")
    log_window.geometry("850x600")  # Adjust size as needed for new controls

    log_window.attributes('-topmost', True)

    def update_log_display():
        selected_network = network_var.get()
        filter_by_date = date_filter_var.get()
        start_datetime_str = start_date_var.get()
        end_datetime_str = end_date_var.get()

        text_area.config(state='normal')
        text_area.delete(1.0, tk.END)  # Clear current log display

        with open("network_status.log", "r") as log_file:
            for line in log_file:
                if selected_network != "All Networks" and selected_network not in line:
                    continue

                if filter_by_date:
                    try:
                        log_datetime_str = line.split(" - ")[0]
                        log_datetime = datetime.datetime.strptime(log_datetime_str, "%Y-%m-%d %H:%M:%S")
                        start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")
                        end_datetime = datetime.datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M")
                        if not (start_datetime <= log_datetime <= end_datetime):
                            continue
                    except ValueError:
                        continue  # Skip entries that don't match the format or are out of the selected range

                text_area.insert(tk.END, line)

        text_area.config(state='disabled')

    # Frame for date/time filter controls
    filter_frame = ttk.Frame(log_window)
    filter_frame.pack(padx=10, pady=(5, 0), fill='x')

    date_filter_var = BooleanVar(value=False)
    start_date_var = StringVar()
    end_date_var = StringVar()

    date_filter_check = ttk.Checkbutton(filter_frame, text="Date/Time", variable=date_filter_var,
                                        command=update_log_display)
    date_filter_check.pack(side=tk.LEFT)

    # Start Date and Time Selection
    ttk.Label(filter_frame, text="Start Date:").pack(side=tk.LEFT, padx=(10, 2))
    start_date_entry = DateEntry(filter_frame, textvariable=start_date_var, width=12)
    start_date_entry.pack(side=tk.LEFT, padx=(2, 10))

    ttk.Label(filter_frame, text="Start Time:").pack(side=tk.LEFT, padx=(10, 2))
    start_hour_var = tk.StringVar(value='00')
    start_minute_var = tk.StringVar(value='00')
    start_hour_spinbox = ttk.Spinbox(filter_frame, from_=0, to=23, wrap=True, textvariable=start_hour_var, width=3,
                                     format="%02.0f")
    start_hour_spinbox.pack(side=tk.LEFT, padx=(2, 2))
    ttk.Label(filter_frame, text=":").pack(side=tk.LEFT)
    start_minute_spinbox = ttk.Spinbox(filter_frame, from_=0, to=59, wrap=True, textvariable=start_minute_var, width=3,
                                       format="%02.0f")
    start_minute_spinbox.pack(side=tk.LEFT, padx=(2, 10))

    # End Date and Time Selection
    ttk.Label(filter_frame, text="End Date:").pack(side=tk.LEFT, padx=(10, 2))
    end_date_entry = DateEntry(filter_frame, textvariable=end_date_var, width=12)
    end_date_entry.pack(side=tk.LEFT, padx=(2, 10))

    ttk.Label(filter_frame, text="End Time:").pack(side=tk.LEFT, padx=(10, 2))
    end_hour_var = tk.StringVar(value='23')
    end_minute_var = tk.StringVar(value='59')
    end_hour_spinbox = ttk.Spinbox(filter_frame, from_=0, to=23, wrap=True, textvariable=end_hour_var, width=3,
                                   format="%02.0f")
    end_hour_spinbox.pack(side=tk.LEFT, padx=(2, 2))
    ttk.Label(filter_frame, text=":").pack(side=tk.LEFT)
    end_minute_spinbox = ttk.Spinbox(filter_frame, from_=0, to=59, wrap=True, textvariable=end_minute_var, width=3,
                                     format="%02.0f")
    end_minute_spinbox.pack(side=tk.LEFT, padx=(2, 10))

    # Dropdown for network selection
    network_var = tk.StringVar()
    network_dropdown = ttk.Combobox(log_window, textvariable=network_var,
                                    values=["All Networks"] + list(networks.keys()))
    network_dropdown.pack(padx=10, pady=(5, 0))
    network_dropdown.set("All Networks")  # Default selection

    text_area = tk.Text(log_window, wrap='word', font=('Helvetica', 10))
    text_area.pack(padx=10, pady=(5, 10), fill='both', expand=True)

    # Call update_log_display when the selection changes
    network_var.trace('w', lambda *args: update_log_display())
    date_filter_var.trace('w', lambda *args: update_log_display())
    start_date_var.trace('w', lambda *args: update_log_display())
    end_date_var.trace('w', lambda *args: update_log_display())

    update_log_display()  # Initial log display update

    # Export filtered log
    def export_filtered_log():
        selected_network = network_var.get()
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"filtered_network_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        )
        if filename:
            with open(filename, "w") as file:
                with open("network_status.log", "r") as log_file:
                    for line in log_file:
                        # Filter based on the selected network, skip if not matching
                        if selected_network != "All Networks" and selected_network not in line:
                            continue
                        file.write(line)
            notification.notify(
                title="Log Exported",
                message=f"Filtered log has been exported as {filename}",
                app_name="Network Status Monitor"
            )

    button_frame = ttk.Frame(log_window)
    button_frame.pack(pady=10, fill=tk.X, padx=10)

    export_button = ttk.Button(button_frame, text="Export Filtered Log", command=export_filtered_log)
    export_button.pack(side=tk.LEFT, padx=5)

    ok_button = ttk.Button(button_frame, text="Close", command=log_window.destroy)
    ok_button.pack(side=tk.RIGHT, padx=5)
def open_terminal():
    terminal_window = tk.Toplevel(window)
    terminal_window.title("Ping Terminal")

    terminal_window.attributes('-topmost', True)

    ttk.Label(terminal_window, text="Select Network Location:").pack(pady=(10, 0))

    # Dropdown for selecting the network location
    location_var = tk.StringVar()
    location_dropdown = ttk.Combobox(terminal_window, textvariable=location_var, values=list(networks.keys()))
    location_dropdown.pack(pady=5)

    ttk.Label(terminal_window, text="Number of Cycles (0 for continuous):").pack()

    cycles_var = tk.StringVar(value='0')
    cycles_entry = ttk.Entry(terminal_window, textvariable=cycles_var, width=5)
    cycles_entry.pack(pady=5)

    # Instruction for the user
    instruction_label = ttk.Label(terminal_window, text="Enter '0' for continuous ping.", font=('Helvetica', 8, 'italic'))
    instruction_label.pack(pady=(0, 10))

    # Define custom_ping function before the button that uses it
    def custom_ping():
        location = location_var.get()
        cycles = cycles_var.get()
        if location:
            ip_address = networks[location]
            if cycles.isdigit():
                cycles = int(cycles)
                # Prepare ping command based on cycles
                command = f"ping -n {cycles} {ip_address}" if cycles > 0 else f"ping -t {ip_address}"
                # Execute ping command and capture output
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                # Open a Toplevel window to display output
                output_window = tk.Toplevel(window)
                output_window.title(f"Ping Output - {location}")
                output_window.attributes('-topmost', True)  # Make this window always on top
                text_area = tk.Text(output_window, wrap='word', font=('Helvetica', 10))
                text_area.pack(padx=10, pady=(10, 0), fill='both', expand=True)

                # Button Frame
                button_frame = tk.Frame(output_window)
                button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

                # Function to asynchronously update the text area with ping output
                def update_output():
                    for line in process.stdout:
                        text_area.insert(tk.END, line)
                        text_area.yview(tk.END)  # Auto-scroll
                    process.wait()
                    text_area.insert(tk.END, "Ping process completed.")

                # Close Button Function
                def close_output_window():
                        output_window.destroy()

                # Close Button
                close_button = tk.Button(button_frame, text="Close", command=close_output_window)
                close_button.pack(side=tk.RIGHT)

                # Start the update_output function in a new thread to keep UI responsive
                threading.Thread(target=update_output, daemon=True).start()
            else:
                tk.messagebox.showerror("Error", "Please enter a valid number of cycles.")
        else:
            tk.messagebox.showerror("Error", "Please select a location.")

    ping_button = ttk.Button(terminal_window, text="Ping", command=custom_ping)
    ping_button.pack(pady=(10, 0))

 # OK Button to close the terminal window
    ok_button = ttk.Button(terminal_window, text="Close", command=lambda: terminal_window.destroy())
    ok_button.pack(pady=10)

# Ping Function
import re


def ping_address(ip_address, max_retries=3):
    num_requests    = int(echo_request_var.get())
    timeout_seconds = int(timeout_var.get())
    success_count   = 0
    latencies       = []
    error_message   = None

    for attempt in range(max_retries):
        response = subprocess.run(
            ["ping", "-n", str(num_requests), "-w", str(timeout_seconds * 1000), ip_address],
            capture_output=True, text=True
        )

        # Always grab any time=<n>ms values
        success_lines = re.findall(r"time=(\d+)ms", response.stdout)
        for ms in success_lines:
            latencies.append(int(ms))
        success_count += len(success_lines)

        if response.returncode != 0:
            # real ping‐failure
            error_message = response.stderr.strip() or "Ping process failed."
            break
        elif success_count > 0:
            # we got at least one good reply
            break

    # If we never saw a time=<n>ms and no ping error, store the raw output
    if success_count == 0 and error_message is None:
        # show the first line or entire stdout
        error_message = response.stdout.strip().splitlines()[0]

    # Compute stats
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
    else:
        avg_latency = min_latency = max_latency = None

    success_rate = (success_count / (num_requests * max_retries)) * 100

    return {
        "online": success_count > 0,
        "success_rate": success_rate,
        "average_latency": avg_latency,
        "min_latency": min_latency,
        "max_latency": max_latency,
        "error_message": error_message,
        "attempts": attempt + 1
    }



# Notification Function
def notify_status_change(name, online, prev_status):
    message = f"{name} changed status from {'offline to online' if prev_status else 'online to offline'}."
    notification.notify(
        title="Network Status Change",
        message=message,
        app_name="Network Status Monitor"
    )

# Update Status Function
def update_status():
    for name, ip in networks.items():
        result = ping_address(ip)
        online = result["online"]

        # Only show Online or Offline
        status_labels[name].config(
            text="Online" if online else "Offline",
            style="Online.TLabel" if online else "Offline.TLabel"
        )

        # Trigger notification on status change
        if prev_status[name] is not None and prev_status[name] != online:
            notify_status_change(name, online, prev_status[name])
        prev_status[name] = online

    # Schedule next run
    try:
        ms = int(update_interval_var.get()) * 1000
    except ValueError:
        ms = 30000
    window.after(ms, update_status)


# GUI Layout
header = ttk.Label(window, text="Network Status Monitor", style="Header.TLabel")
header.pack(pady=10)

# Ping Settings Frame
#ping_settings_frame = ttk.LabelFrame(window, text="Ping Settings", padding=(10, 5))
#ping_settings_frame.pack(pady=10, padx=10, fill='x')

# Echo Requests Entry
#ttk.Label(ping_settings_frame, text="Echo Requests:").pack(side=tk.LEFT)
#echo_request_entry = ttk.Entry(ping_settings_frame, textvariable=echo_request_var, width=5)
#echo_request_entry.pack(side=tk.LEFT, padx=(0, 10))

# Timeout Entry
#ttk.Label(ping_settings_frame, text="Timeout (seconds):").pack(side=tk.LEFT)
#timeout_entry = ttk.Entry(ping_settings_frame, textvariable=timeout_var, width=5)
#timeout_entry.pack(side=tk.LEFT)

# Network Status Section Adjustment
network_status_frame = ttk.Frame(window)
network_status_frame.pack(pady=10, padx=10, fill='x')

row = 0
for name in networks.keys():
    network_label = ttk.Label(network_status_frame, text=f"{name}:", font=('Helvetica', 10))
    network_label.grid(row=row, column=0, sticky="W", padx=5)

    status_label = ttk.Label(network_status_frame, text="Checking...", font=('Helvetica', 10))
    status_label.grid(row=row, column=1, sticky="E", padx=5)
    status_labels[name] = status_label

    row += 1

# Create a frame for buttons to ensure they are aligned in the same line
buttons_frame = ttk.Frame(window)
buttons_frame.pack(pady=20, padx=10, fill='x')

# "Update Now" Button
#update_button = ttk.Button(buttons_frame, text="Update Now", command=update_status)
#update_button.pack(side=tk.LEFT, padx=5, expand=True)

# "View Log" Button
view_log_button = ttk.Button(buttons_frame, text="View Log", command=view_log)
view_log_button.pack(side=tk.LEFT, padx=5, expand=True)

# "Open Terminal" Button
terminal_button = ttk.Button(buttons_frame, text="Ping a Network", command=open_terminal)
terminal_button.pack(side=tk.LEFT, padx=5, expand=True)


# Gear Button to open the Settings Page
settings_button = ttk.Button(window, image=gear_icon, command=lambda: open_settings_page())
settings_button.place(relx=1.0, rely=0.0, anchor='ne')

def apply_settings():
    try:
        # Attempt to convert the update interval to an integer
        new_interval = int(update_interval_var.get())

        # Validate the new interval is within an acceptable range
        if 5 <= new_interval <= 3600:
            # If validation passes, apply the new interval
            # This could involve updating global variables, configuration files, etc.
            # Since update_interval_var is directly used for scheduling in update_status,
            # updating it is enough to apply the new setting.

            # Optionally: Save settings to a file for persistence across sessions (not shown here)

            # Close the settings window
            settings_window.destroy()
        else:
            # If the new interval is out of range, show an error message
            tk.messagebox.showerror("Error", "Update interval must be between 5 and 3600 seconds.")
    except ValueError:
        # If conversion to integer fails, show an error message
        tk.messagebox.showerror("Error", "Invalid input. Please enter a valid number for the update interval.")

# Function to open the Settings Page
def open_settings_page():
    settings_window = tk.Toplevel(window)
    settings_window.title("Settings")
    settings_window.geometry("400x360")
    settings_window.attributes('-topmost', True)

    frm = ttk.Frame(settings_window, padding=10)
    frm.pack(fill='both', expand=True)

    cols = ("Name", "IP")
    tree = ttk.Treeview(frm, columns=cols, show='headings', height=8)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=150, anchor='center')
    tree.grid(row=0, column=0, columnspan=3, pady=(0,10))

    for name, ip in networks.items():
        tree.insert('', 'end', iid=name, values=(name, ip))

    def on_add():
        dlg = tk.Toplevel(settings_window)
        dlg.title("Add Entry")
        dlg.transient(settings_window)  # Keep on top of Settings
        dlg.grab_set()                  # Modal: block input to Settings

        tk.Label(dlg, text="Name:").grid(row=0, column=0, sticky='e')
        tk.Label(dlg, text="IP:").grid(row=1, column=0, sticky='e')
        nm = tk.Entry(dlg); nm.grid(row=0, column=1, padx=5, pady=2)
        ip = tk.Entry(dlg); ip.grid(row=1, column=1, padx=5, pady=2)

        def add_confirm():
            n = nm.get().strip(); i = ip.get().strip()
            if not n or not i:
                messagebox.showerror("Error","Name and IP required.", parent=dlg)
                return
            if n in networks:
                messagebox.showerror("Error","Name already exists.", parent=dlg)
                return
            networks[n] = i
            tree.insert('', 'end', iid=n, values=(n,i))
            dlg.destroy()

        tk.Button(dlg, text="Add", command=add_confirm).grid(row=2, column=0, columnspan=2, pady=5)

    def on_edit():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Info","Select one entry to edit.", parent=settings_window)
            return
        old = sel[0]
        old_ip = networks[old]

        dlg = tk.Toplevel(settings_window)
        dlg.title("Edit Entry")
        dlg.transient(settings_window)  # Keep on top of Settings
        dlg.grab_set()                  # Modal

        tk.Label(dlg, text="Name:").grid(row=0, column=0, sticky='e')
        tk.Label(dlg, text="IP:").grid(row=1, column=0, sticky='e')
        nm = tk.Entry(dlg); nm.insert(0, old); nm.grid(row=0, column=1, padx=5, pady=2)
        ip = tk.Entry(dlg); ip.insert(0, old_ip); ip.grid(row=1, column=1, padx=5, pady=2)

        def edit_confirm():
            n = nm.get().strip(); i = ip.get().strip()
            if not n or not i:
                messagebox.showerror("Error","Name and IP required.", parent=dlg)
                return
            if n != old and n in networks:
                messagebox.showerror("Error","Name already exists.", parent=dlg)
                return
            # Update dict & tree
            del networks[old]
            tree.delete(old)
            networks[n] = i
            tree.insert('', 'end', iid=n, values=(n,i))
            dlg.destroy()

        tk.Button(dlg, text="Save", command=edit_confirm).grid(row=2, column=0, columnspan=2, pady=5)

    def on_remove():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select an entry to remove.", parent=settings_window)
            return
        if not messagebox.askyesno("Confirm Removal", "Remove selected address(es)?", parent=settings_window):
            return
        for iid in sel:
            tree.delete(iid)
            networks.pop(iid, None)

    ttk.Button(frm, text="Add",    command=on_add).grid(row=1, column=0, sticky='ew', padx=5)
    ttk.Button(frm, text="Edit",   command=on_edit).grid(row=1, column=1, sticky='ew', padx=5)
    ttk.Button(frm, text="Remove", command=on_remove).grid(row=1, column=2, sticky='ew', padx=5)

    # (Echo/Timeout/Interval fields here…)

    def apply_and_close():
        # Rebuild status labels…
        for widget in network_status_frame.winfo_children():
            widget.destroy()
        status_labels.clear()
        row = 0
        for nm, ip in networks.items():
            ttk.Label(network_status_frame, text=f"{nm}:", font=('Helvetica',10))\
                .grid(row=row, column=0, sticky="W", padx=5)
            lbl = ttk.Label(network_status_frame, text="Checking...", font=('Helvetica',10))
            lbl.grid(row=row, column=1, sticky="E", padx=5)
            status_labels[nm] = lbl
            prev_status[nm] = None
            row += 1
        settings_window.destroy()

    ttk.Button(frm, text="Apply", command=apply_and_close)\
        .grid(row=5, column=0, columnspan=3, pady=20, sticky='ew')
    frm.columnconfigure((0,1,2), weight=1)


# Start the periodic update in a separate thread
threading.Thread(target=update_status, daemon=True).start()

window.mainloop()
