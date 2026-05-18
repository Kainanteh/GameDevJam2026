import os
import zipfile

def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Ensure the path in zip is relative to folder_path (so index.html is at root)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    print(f"Successfully zipped {folder_path} to {zip_path}")

if __name__ == '__main__':
    zip_directory("/home/kainanteh/game-dev-jam-2026/build", "/home/kainanteh/game-dev-jam-2026/game-dev-jam-web.zip")
