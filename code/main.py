
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import csv
import os
from pathlib import Path
import threading  # Added to prevent the GUI from freezing

# Hidden root window so a blank app doesn't stay open
root = tk.Tk()
root.withdraw() 

# 1. This opens a pop-up and waits for the user to type
user_input = simpledialog.askstring("File Extension Finder", "Put a file extension to find in C drive (the dot doesn't matter if it is there or not.):")
# If cancel button is pressed, exit the program to avoid empty spreadsheet files.
if user_input is None:
    print("User cancelled the input. Exiting the program.")
    exit()

csv_name = simpledialog.askstring("File Extension Finder", "What would you like to name the spreadsheet file? (e.g., 'my_files.csv')")
if csv_name is None:
    print("User cancelled the input. Exiting the program.")
    exit()

# Make sure the filename ends with .csv
if not csv_name.lower().endswith('.csv'):
    csv_name += '.csv'

print(f"User typed: {user_input} and the spreadsheet will be named: {csv_name}")

def find_file_by_extension_csv(extension, loading_window, progress_bar, status_label):
    try:
        extension = extension.strip()
        if not extension:
            raise ValueError("Please enter a file extension, such as pdf or .pdf.")
        if not extension.startswith('.'):
            extension = '.' + extension

        c_drive = Path("C:/")
        matches = []

        # Create spreadsheets directory if it doesn't exist
        output_dir = Path(__file__).resolve().parent / "spreadsheets"
        output_dir.mkdir(exist_ok=True)
        output_csv = output_dir / csv_name

        print(f"Scanning C drive for files with {extension}...")
        print(f"Saving spreadsheet to: {output_csv.absolute()}\n")

        # Open the CSV file for writing
        with output_csv.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            
            # Write the column headers at the very top of the spreadsheet
            writer.writerow(["File Name", "Size (MB)", "Full Folder Path"])

            def ignore_scan_error(_error):
                pass

            for folder_path, folder_names, file_names in os.walk(
                c_drive, onerror=ignore_scan_error
            ):
                folder_names[:] = [
                    folder_name for folder_name in folder_names
                    if folder_name.lower() != "windows"
                ]

                for file_name in file_names:
                    if not file_name.endswith(extension):
                        continue

                    file_path = Path(folder_path) / file_name
                    try:
                        if file_path.is_file():
                            matches.append(file_path)

                            # Calculate size in MB (bytes / 1024 / 1024)
                            size_in_mb = file_path.stat().st_size / (1024 * 1024)
                            writer.writerow([file_path.name, f"{size_in_mb:.2f}", file_path.parent])

                            if len(matches) % 100 == 0:
                                print(f" scanning... Logged {len(matches)} files to the spreadsheet...")
                                # Safely update the loading window text from the background thread
                                status_label.config(text=f"Scanning... Found {len(matches)} files")

                    except (OSError, PermissionError):
                        continue

        print(f"\nScan complete. Found {len(matches)} files total.")
        print(f"Spreadsheet saved successfully as '{output_csv}'.")
        
        # Close the loading window and stop the bar when finished
        progress_bar.stop()
        loading_window.destroy()
        
        # Show completion popup
        messagebox.showinfo("Scan Complete", f"Found {len(matches)} files with the extension '{extension}'.\nSpreadsheet saved as '{output_csv}'.")
        root.quit()  # Cleanly exit the script background window

    except Exception as error:
        # If anything goes wrong, close the loading screen and show the error
        progress_bar.stop()
        loading_window.destroy()
        messagebox.showerror("An error occurred. Check the terminal for more information.", str(error))
        print(error)
        root.quit()

def create_loading_screen():
    # Create a nice floating pop-up window for the progress bar
    loading_window = tk.Toplevel()
    loading_window.title("Scanning C Drive")
    loading_window.geometry("350x120")
    
    # Keeps the user from clicking behind this window while it works
    loading_window.grab_set() 

    status_label = tk.Label(loading_window, text="Initializing file scan...", font=("Arial", 10))
    status_label.pack(pady=15)

    # Indeterminate progress bar (bounces back and forth)
    progress_bar = ttk.Progressbar(loading_window, orient="horizontal", length=280, mode="indeterminate")
    progress_bar.pack(pady=5)
    progress_bar.start(10)  # Start animating immediately

    # Start the scanning function inside a background thread so the window remains active
    scan_thread = threading.Thread(
        target=find_file_by_extension_csv, 
        args=(user_input, loading_window, progress_bar, status_label)
    )
    scan_thread.daemon = True  # Allows closing the program instantly if closed manually
    scan_thread.start()

# Start the process
create_loading_screen()
root.mainloop()
