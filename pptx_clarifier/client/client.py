import requests
from pptx_clarifier.definitions import base_url
from pptx_clarifier.client import client_logger as logger
from pptx_clarifier.client.Status import Status


def upload(pptx_path: str) -> str:
    # Open the file to be sent
    with open(pptx_path, 'rb') as file:
        # Create a dictionary containing the file data
        files = {'file': file}

        # Send a POST request with the file
        response = requests.post(f"{base_url}/upload", files=files)

        if response.status_code == 200:
            return response.json()['file_uuid']
        else:
            raise Exception(f"Error uploading file: {response.json()['message']}")


def status(file_uuid: str) -> Status:
    # Send a GET request to the server
    logger.info(f"send status request with uid: {file_uuid}")
    response = requests.get(f"{base_url}/status", params={'file_uuid': file_uuid})

    if response.status_code < 300:
        res_status = Status(response)
        logger.info(f"file found with status: {res_status.status}")
        return res_status
    else:
        raise Exception(f"Error getting status: {response.json()['message']}")
