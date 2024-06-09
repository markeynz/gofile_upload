import os
import requests
import shutil
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor

def get_server():
    """Get the server for uploading the file."""
    response = requests.get("https://api.gofile.io/getServer")
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'ok':
            return data['data']['server']
        else:
            raise Exception("Error in getting server: {}".format(data['status']))
    else:
        response.raise_for_status()

def upload_file(file_path):
    """Upload the file to GoFile.io."""
    server = get_server()
    upload_url = f"https://{server}.gofile.io/uploadFile"

    def create_callback(encoder):
        encoder_len = encoder.len
        def callback(monitor):
            progress = monitor.bytes_read / encoder_len
            print(f"\rUploading {os.path.basename(file_path)}: {progress:.2%}", end="")
        return callback

    with open(file_path, 'rb') as f:
        encoder = MultipartEncoder(fields={'file': (os.path.basename(file_path), f, 'application/octet-stream')})
        monitor = MultipartEncoderMonitor(encoder, create_callback(encoder))
        response = requests.post(upload_url, data=monitor, headers={'Content-Type': monitor.content_type})

    print()  # For newline after the progress output

    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'ok':
            return data['data']
        else:
            raise Exception("Error in uploading file: {}".format(data['status']))
    else:
        response.raise_for_status()

def upload_files_in_folder(folder_path):
    """Upload all files in the specified folder to GoFile.io."""
    if not os.path.isdir(folder_path):
        raise ValueError(f"{folder_path} is not a valid directory.")
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        dest_path = os.path.join(destination_path, filename)
        if os.path.isfile(file_path):
            try:
                result = upload_file(file_path)
                print({filename})
                print(result['downloadPage'])
                print()
                shutil.move(file_path,dest_path)
            except Exception as e:
                print(f"An error occurred while uploading '{filename}': {e}")
        else:
            print(f"'{filename}' is not a file, skipping...")

if __name__ == "__main__":
    folder_path = ""  # Replace with the path to your uploads folder
    destination_path = ""  # Replace with the path to your completed folder
    upload_files_in_folder(folder_path)
