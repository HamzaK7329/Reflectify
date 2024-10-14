import os
import shutil
import time

# Paths for folders
downloads_folder = os.path.expanduser('~/Downloads')
pictures_folder = os.path.expanduser('~/Downloads/Pictures')
pdfs_folder = os.path.expanduser('~/Downloads/PDFs')

# Create directories (if they don' exist)
os.makedirs(pictures_folder, exist_ok=True)
os.makedirs(pdfs_folder, exist_ok=True)

# File types
file_types = {
    'Pictures': ['.jpg', '.jpeg', '.png', '.gif'],
    'PDFs': ['.pdf']
}

def move_file(file_path, target_folder):
    try:
        shutil.move(file_path, target_folder)
        print(f'Moved: {file_path} to {target_folder}')
    except Exception as e:
        print(f'Error moving {file_path}: {e}')

def organize_and_move(file_name):
    file_path = os.path.join(downloads_folder, file_name)
    file_extension = os.path.splitext(file_name)[1].lower()

    # Check if downloaded file is a picture
    if file_extension in file_types['Pictures']:
        move_file(file_path, pictures_folder)

    # Check if downloaded file is a PDF
    elif file_extension in file_types['PDFs']:
        move_file(file_path, pdfs_folder)

    else:
        print(f'File {file_name} does not match any categories (Skipping).')

def monitor_folder():
    print("Monitoring downloads folder...")
    while True:
        # List files in the downloads folder
        files_in_downloads = os.listdir(downloads_folder)

        for file_name in files_in_downloads:
            # Skip if it's a folder
            if os.path.isdir(os.path.join(downloads_folder, file_name)):
                continue

            # Move file based on type
            organize_and_move(file_name)
        
        # Wait 5 seconds before scanning again
        time.sleep(5)

if __name__ == "__main__":
    monitor_folder()

