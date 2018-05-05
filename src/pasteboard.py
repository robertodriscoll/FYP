#!/usr/bin/python3
import requests, json, os

def upload_image_file( file_to_upload ):

    file_name, file_extension = os.path.splitext( file_to_upload )
    files = {'file': (file_to_upload, open(file_to_upload, 'rb'), 
            file_extension[1:], {'Expires': '0'})}

    response = requests.post('https://pasteboard.co/upload',  files=files)

    json_data = json.loads(response.text)

    return json_data['url']