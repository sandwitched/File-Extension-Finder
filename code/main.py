import csv
import os
from pathlib import Path

def find_file_by_extension_csv(extension):

    extension = extension.strip()
    if not extension:
        raise ValueError("Please enter a file extension, such as pdf or .pdf.")
    if not extension.startswith('.'):
        extension = '.' + extension

    file_pattern = f"*{extension}"

    c_drive = Path("C:/")
    matches = []
    
    # 1. Create a spreadsheet file (.csv)
    output_csv = Path("organised_files.csv")

    print(f"Scanning C drive for files with {extension}...")
    print(f"Saving spreadsheet to: {output_csv.absolute()}\n")

    # Open the CSV file for writing
    with output_csv.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        
        # 2. Write the column headers at the very top of the spreadsheet
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

                except (OSError, PermissionError):
                    continue

    print(f"\nScan complete. Found {len(matches)} files total.")
    print(f"google spreadsheet saved successfully as '{output_csv}'.")
    return matches

extension = input("Enter file extension to find in c drive: ")
try:
    find_file_by_extension_csv(extension)
except ValueError as error:
    print(error)

