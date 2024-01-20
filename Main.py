import tkinter as tk
import tkinter.font as tkFont
import subprocess
from subprocess import Popen, PIPE
import threading
import queue
import json
import re
import os

config_file = 'miner_config.json'

# Global reference to the mining process
mining_process = None

# Global flag to indicate intentional termination
stop_requested = False


def strip_ansi_codes(text):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


def save_config():
    config = {
        'poolurl': poolurl_entry.get(),
        'username': username_entry.get(),
        'threads': threads_entry.get(),
        'other': other_entry.get()
    }
    with open(config_file, 'w') as file:
        json.dump(config, file)


def load_config():
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
            poolurl_entry.insert(0, config.get('poolurl', ''))
            username_entry.insert(0, config.get('username', ''))
            threads_entry.insert(0, config.get('threads', ''))
            other_entry.insert(0, config.get('other', ''))
    except FileNotFoundError:
        pass


def execute_command(cmd, output_queue):
    global mining_process, stop_requested
    try:
        startupinfo = None
        if os.name == 'nt':  # If running on Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        mining_process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                          startupinfo=startupinfo)

        # Continuously read output
        while True:
            line = mining_process.stdout.readline()
            if line:
                output_queue.put(line)
            else:
                break

        return_code = mining_process.wait()
        if return_code and not stop_requested:
            output_queue.put(f"Process exited with return code {return_code}")

    except subprocess.CalledProcessError as e:
        output_queue.put(f"Exception: {str(e)}")
    finally:
        stop_requested = False
        update_mining_status("Status: Not Mining")


def update_output_textbox(output_queue):
    try:
        line = output_queue.get_nowait()
        clean_line = strip_ansi_codes(line)
        output_textbox.insert(tk.END, clean_line)
        output_textbox.see(tk.END)
    except queue.Empty:
        pass
    finally:
        root.after(100, update_output_textbox, output_queue)


def update_mining_status(message):
    if isinstance(message, bool):
        message = "Status: Mining" if message else "Status: Not Mining"
    fg_color = "red" if "Error:" in message or "Exception:" in message or "Process exited" in message else "green"
    status_label.config(text=message, fg=fg_color)

#def update_mining_status(running):
#    if running:
#        status_label.config(text="Status: Mining", fg="green")
#    else:
#        status_label.config(text="Status: Not Mining", fg="red")


def start_mining():
    global mining_process
    if mining_process is None or mining_process.poll() is not None:
        # Clear the output textbox only if mining is not already in progress
        output_textbox.delete("1.0", tk.END)
    # Clear the output textbox
    output_textbox.delete("1.0", tk.END)

    # Retrieve values from text boxes
    poolurl = poolurl_entry.get()
    username = username_entry.get()
    threads = threads_entry.get()
    other = other_entry.get()

    # Construct the command
    command = f"cpuminer-avx2-sha -a yespower -o {poolurl} -u {username} -t {threads} {other}"
    print("Executing:", command)  # For demonstration

    # Start the command in a new thread
    output_queue = queue.Queue()
    threading.Thread(target=execute_command, args=(command, output_queue), daemon=True).start()
    update_output_textbox(output_queue)
    update_mining_status("Status: Mining")


def stop_mining():
    global mining_process, stop_requested
    stop_requested = True  # Set the flag when stopping
    if mining_process:
        mining_process.terminate()
        mining_process.wait(5)
        mining_process = None
        output_textbox.insert(tk.END, "Mining stopped.\n")
    update_mining_status("Status: Not Mining")


def on_closing():
    global mining_process
    if mining_process:
        # Terminate the process using its PID
        try:
            mining_process.terminate()
            mining_process.wait(5)  # Wait for 5 seconds to allow process to terminate
        except Exception as e:
            print("Error terminating process:", e)
    root.destroy()  # Close the GUI


# Create the main window
root = tk.Tk()
root.title("Veco GUI miner")

# Customizing font
custom_font = tkFont.Font(family="Helvetica", size=10, weight="bold")

# Create and place labels, entry widgets, and the output textbox
tk.Label(root, text="Mining pool URL with port (stratum+tcp://...):").grid(row=0, column=0)
poolurl_entry = tk.Entry(root, width=50)
poolurl_entry.grid(row=0, column=1)

tk.Label(root, text="Username (e.g. wallet):").grid(row=1, column=0)
username_entry = tk.Entry(root, width=50)
username_entry.grid(row=1, column=1)

tk.Label(root, text="Threads (not required):").grid(row=2, column=0)
threads_entry = tk.Entry(root, width=5)
threads_entry.grid(row=2, column=1)

tk.Label(root, text="Other options e.g. difficulty, password (not required):").grid(row=3, column=0)
other_entry = tk.Entry(root, width=50)
other_entry.grid(row=3, column=1)

# Create and place the "Save config" button
save_button = tk.Button(root, text="Save as default", command=save_config, width=50)
save_button.grid(row=4, columnspan=3)

# Create and place the output textbox
output_textbox = tk.Text(root, bg='black', fg='white')
output_textbox.grid(row=5, column=0, columnspan=2, sticky='nsew')

# Create tags for 'Accepted' and 'Rejected' words
#output_textbox.tag_config("accepted", foreground="green")
#output_textbox.tag_config("rejected", foreground="red")

# Configure the grid to allow resizing
root.grid_rowconfigure(3, weight=1)  # Allow row 3 (where the textbox is) to resize
root.grid_columnconfigure(1, weight=1)  # Allow column 1 to resize

# Create and place the "mine" button with custom color and font
mine_button = tk.Button(root, text="Mine", command=start_mining, bg="green", font=custom_font, width=50)
mine_button.grid(row=6, column=0, columnspan=1)

# Create and place the "Stop" button with custom color and font
stop_button = tk.Button(root, text="Stop", command=stop_mining, bg="red", font=custom_font, width=50)
stop_button.grid(row=6, column=1, columnspan=1)

# Status label
status_label = tk.Label(root, text="Status: Not Mining", font=custom_font)
status_label.grid(row=7, column=0, columnspan=2)

# Load the configuration at startup
load_config()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI event loop
root.mainloop()

