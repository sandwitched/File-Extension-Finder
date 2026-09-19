from pathlib import Path

def find_file_by_extension_csv(extension):

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
    with output_csv.open("w", encoding="utf-8") as csv_file:
        
        # 2. Write the column headers at the very top of the spreadsheet
        csv_file.write("File Name,Size (MB),Full Folder Path\n")

        for file_path in c_drive.rglob(file_pattern):
            if "Windows" in file_path.parts:
                continue
                
            try:
                if file_path.is_file():
                    matches.append(file_path)
                    
                    # 3. Gather information about the file using pathlib tools
                    file_name = file_path.name
                    folder_path = file_path.parent
                    
                    # Calculate size in MB (bytes / 1024 / 1024)
                    size_in_mb = file_path.stat().st_size / (1024 * 1024)
                    
                    # 4. Clean the data to make sure commas in filenames don't break the CSV columns
                    clean_name = f'"{file_name}"'
                    clean_folder = f'"{folder_path}"'
                    
                    # Write the row data separated by commas
                    csv_file.write(f"{clean_name},{size_in_mb:.2f},{clean_folder}\n")
                    
                    # Progress tracker
                    if len(matches) % 100 == 0:
                        print(f" scanning... Logged {len(matches)} files to the spreadsheet...")

            except PermissionError: 
                continue

    print(f"\nScan complete. Found {len(matches)} files total.")
    print(f"google spreadsheet saved successfully as '{output_csv}'.")
    return matches

extension = input("Enter file extension to find in c drive: ")
find_file_by_extension_csv(extension)

