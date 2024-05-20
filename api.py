import requests


class APIManager:
    BASE_URL = 'http://web:8000/api/'
    ROOMS_ENDPOINT = BASE_URL + 'rooms/'
    DEVICE_ENDPOINT = BASE_URL + 'devices/'
    SENSORS_ENDPOINT = BASE_URL + 'sensors/'
    ACTIONS_ENDPOINT = BASE_URL + 'actions/'
    COMMAND_ENDPOINT = BASE_URL + 'command/'
    
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return "Connection to server failed. Try again later.", 500



def send_command(sensor, command):
    url = APIManager.COMMAND_ENDPOINT
    headers = {'Content-Type': 'application/json'}
    data = {
        "sensor_id": sensor['id'],
        "command": command
    }

    response = requests.post(url, headers=headers, json=data)
    return response.text


def flash_device(id, ssid, password, ip):
    required_fields_msg = ''
    if not ssid:
        required_fields_msg += 'WiFi SSID is required.\n\n'
    if not password:
        required_fields_msg += 'WiFi Password is required.\n\n'
    if not ip:
        required_fields_msg += 'Server IP is required.'
    
    if required_fields_msg:
        return required_fields_msg, 400

    url = 'http://web:8000/api/flash/' + str(id)
    headers = {'Content-Type': 'application/json'}
    data = {
        "ssid_name": ssid,
        "ssid_password": password,
        "ip_address": ip
    }

    response = requests.post(url, headers=headers, json=data)
    
    return response.text, response.status_code


def get_connected_device():
    url = 'http://web:8000/api/serial/'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception:
        data = None
    return data

def update_device(id, data):
    try:
        response = requests.patch(f"http://web:8000/api/devices/{id}/", data=data)
        response.raise_for_status()
        data = response.json()
    except Exception:
        data = None
    return data

def create_room(data):
    response = requests.post(f"http://web:8000/api/rooms/", data=data)
    data = response.json()
    status = response.status_code
    return data, status

def update_room(id, data):
    response = requests.patch(f"http://web:8000/api/rooms/{id}/", data=data)
    data = response.json()
    status = response.status_code
    return data, status

def delete_room(id):
    response = requests.delete(f"http://web:8000/api/rooms/{id}/")
    return response.status_code

def update_sensor(id, data):
    response = requests.patch(f"http://web:8000/api/sensors/{id}/", data=data)
    data = response.json()
    status = response.status_code
    return data, status

def post_data(url, data):
    response = requests.post(url, data=data)
    # data = response.json()
    print(response)
    status = response.status_code
    return data, status

def make_request(url, id=None, data=None, method='GET'):
    try:
        if method == 'GET':
            response = requests.get(url)
            response_data = response.json()
        elif method == 'POST':
            response = requests.post(url, data=data)
            response_data = response.json()
        elif method == 'PATCH':
            response = requests.patch(url + f'{id}/', data=data)
            response_data = response.json()
        elif method == 'DELETE':
            response = requests.delete(url + f'{id}/')
            response_data = None
    except requests.exceptions.RequestException as e:
        return "Connection to server failed. Try again later.", 500

    return response_data, response.status_code