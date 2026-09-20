import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import csv
import os
from pathlib import Path
import threading # Added to prevent the GUI from freezing
from datetime import date

today = date.today()

# Hidden root window so a blank app doesn't stay open
root = tk.Tk()
root.withdraw()

# Asks the user for the drive letter to scan.
drive_letter = simpledialog.askstring("File Extension Finder", "What drive letter should the app scan in?:")
if drive_letter is None:
    print("User cancelled the input. Exiting the program.")
    exit()

# Checks if the drive letter contains a : or if it even is a valid drive letter
if not drive_letter.endswith(':'):
    drive_letter += ':'
if not os.path.exists(drive_letter + '/'):
    messagebox.showerror("Invalid Drive Letter", f"The drive letter '{drive_letter}' does not exist. Please check and try again.")
    exit()

# 1. This opens a pop-up and waits for the user to type
user_input = simpledialog.askstring("File Extension Finder", "Put a file extension to find in " + drive_letter + " drive (the dot doesn't matter if it is there or not.):")

# If cancel button is pressed, exit the program to avoid empty spreadsheet files.
if user_input is None:
    print("User cancelled the input. Exiting the program.")
    exit()

#auto naming csv file
def auto_name():
    clean_drive = drive_letter.replace(":", "")
    name = f"{user_input}_{clean_drive}Drive_Scan_on_{today}"
    return name

csv_name = simpledialog.askstring("File Extension Finder", "What would you like to name the spreadsheet file? (e.g., 'my_files.csv') or A to auto name")
if csv_name is None:
    print("User cancelled the input. Exiting the program.")
    exit()
elif csv_name == "a" or csv_name == "A":
    csv_name = auto_name()
# Make sure the filename ends with .csv
else:
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
        
        # FIXED: Changed from Path(drive_letter) to include a backslash so Windows scans the entire drive
        drive_path = Path(drive_letter + "\\")
        matches = []
        
        try:
            base_dir = Path(__file__).resolve().parent
        except NameError:
            base_dir = Path(os.getcwd())
            
        # Create spreadsheets directory if it doesn't exist
        output_dir = base_dir / "spreadsheets"
        output_dir.mkdir(exist_ok=True)
        output_csv = output_dir / csv_name
        
        print(f"Scanning the selected drive for files with {extension}...")
        print(f"Saving spreadsheet to: {output_csv.absolute()}\n")
        
        # Open the CSV file for writing
        with output_csv.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            
            # Write the column headers at the very top of the spreadsheet
            writer.writerow(["File Name", "Size (MB)", "Full Folder Path"])
            
            def ignore_scan_error(_error):
                pass
                
            for folder_path, folder_names, file_names in os.walk(
                drive_path, onerror=ignore_scan_error
            ):
                folder_names[:] = [
                    folder_name for folder_name in folder_names if folder_name.lower() != "windows"
                ]
                
                for file_name in file_names:
                    # FIXED: Added lower() back here just in case any files have mixed extensions (.mD / .MD)
                    if not file_name.lower().endswith(extension.lower()):
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
                                
                                current_matches = len(matches)
                                root.after(0, lambda m=current_matches: status_label.config(text=f"Scanning... Found {m} files"))
                                
                    except (OSError, PermissionError):
                        continue
                        
        print(f"\nScan complete. Found {len(matches)} files total.")
        print(f"Spreadsheet saved successfully as '{output_csv}'.")
        
        def complete_ui():
            progress_bar.stop()
            loading_window.destroy()
            messagebox.showinfo("Scan Complete", f"Found {len(matches)} file(s) with the extension '{extension}'.\nSpreadsheet saved as '{output_csv}'. (There may be more file extensions in the Windows directory if there is one.)")
            root.quit()
            
        root.after(0, complete_ui)
        
    except Exception as error:
        def error_ui():
            progress_bar.stop()
            loading_window.destroy()
            messagebox.showerror("An error occurred. Check the terminal for more information.", str(error))
            print(error)
            root.quit()
            
        root.after(0, error_ui)

def create_loading_screen():
    loading_window = tk.Toplevel()
    loading_window.title("Scanning selected drive...")
    loading_window.geometry("350x120")
    loading_window.grab_set()
    
    status_label = tk.Label(loading_window, text="Initializing file scan...", font=("Arial", 10))
    status_label.pack(pady=15)
    
    progress_bar = ttk.Progressbar(loading_window, orient="horizontal", length=280, mode="indeterminate")
    progress_bar.pack(pady=5)
    progress_bar.start(10)
    
    scan_thread = threading.Thread(
        target=find_file_by_extension_csv,
        args=(user_input, loading_window, progress_bar, status_label)
    )
    scan_thread.daemon = True
    scan_thread.start()

create_loading_screen()
root.mainloop()

