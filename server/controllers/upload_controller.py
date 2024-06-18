import os
from flask import jsonify

UPLOAD_DIRECTORY = "/data/uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

def handle_file_upload(file):
    original_filename = file.filename
    upload_path = os.path.join(UPLOAD_DIRECTORY, original_filename)
    
    # Ensure the filename is unique to avoid overwriting an existing file
    counter = 1
    while os.path.exists(upload_path):
        # Splitting the filename from its extension
        name, extension = os.path.splitext(original_filename)
        upload_path = os.path.join(UPLOAD_DIRECTORY, f"{name}_{counter}{extension}")
        counter += 1

    # Save the file to the new or original path
    file.save(upload_path)

    return jsonify({'message': 'File uploaded successfully', 'filePath': upload_path})
