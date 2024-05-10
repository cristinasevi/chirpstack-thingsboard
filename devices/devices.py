import grpc
from chirpstack_api.as_pb.external import api
from datetime import datetime
import time
import openpyxl
import os
import configparser

import requests 

server = "localhost:8080"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiNzYyOGE4NGQtOGRhMy00ZDQ1LWJlNmYtZTM4MWY5MzQ5ZWI1IiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTY3NzY4NzI5NCwic3ViIjoiYXBpX2tleSJ9.LBx46H_nzGPkSxqsqVxU_5ig0soMF9dWlsuA6obE1EY"
Com_Count = 0
last_checked_day = None
Device_List = []
Gateway_List = []

# Leer configuraciones desde config.ini
config = configparser.ConfigParser()
config.read('config.ini')

Comm_Threshold = config['DEFAULT'].getint('Comm_Threshold', 300)  # Convertir a entero, usar 300 por defecto si no se encuentra
Log_Rate = config['DEFAULT'].getint('Log_Rate', 60)  # Convertir a entero, usar 60 por defecto si no se encuentra
Plant_Name = config['DEFAULT'].get('Plant_Name', 'Test')  # Si no se encuentra, usar 'Test' por defecto


def GetDevicesSummary():
    # The API token (retrieved using the web-interface).
    global api_token
    # Connect without using TLS.
    channel = grpc.insecure_channel(server)

    client = api.ApplicationServiceStub(channel)

    # Define the API key meta-data.
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    device = api.ListApplicationRequest()
    device.limit = 10000

    resp = client.List(device, metadata=auth_token)

    device_summaries = {}
    for application in resp.result:
        # Device-queue API client.
        client = api.DeviceServiceStub(channel)

        # Define the API key meta-data.
        auth_token = [("authorization", "Bearer %s" % api_token)]

        # Construct request 
        device = api.ListDeviceRequest()
        device.application_id = application.id
        device.limit = 10000

        resp = client.List(device, metadata=auth_token)

        # Print the downlink frame-counter value.
        for device in resp.result:
            summary = api.GetDeviceRequest()
            summary.dev_eui = device.dev_eui

            # Get the device summary.
            summary = client.Get(summary, metadata=auth_token)

            # Store the device summary in the dictionary.
            device_summaries[device.dev_eui] = summary
            
        print(device_summaries)
    return device_summaries

GetDevicesSummary()

# get /api/internal/devices/summary
def GetDeviceStatus(server, api_token):
    url = f"http://{server}/api/internal/devices/summary"
    headers = {"Authorization": f"Bearer {api_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        summary_data = response.json()
        print("Resumen de información sobre los dispositivos internos:")
        print(summary_data)
    else:
        print("Error al obtener el resumen de información sobre los dispositivos internos:", response.status_code)

GetDeviceStatus(server, api_token)

# get /api/devices/{dev_eui}  
def GetDeviceData(api_token, server, device_id):
    # Define the API endpoint to get data for a specific device.
    url = f"http://{server}/api/devices/{device_id}"

    # Define headers with authorization token.
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Make a GET request to the API endpoint.
    response = requests.get(url, headers=dict(auth_token))

    # Check if the request was successful.
    if response.status_code == 200:
        # Parse the response JSON.
        device_data = response.json()
        return device_data
    else:
        # Print error message if request failed.
        print(f"Failed to get device data: {response.text}")
        return None

device_id = "0004a30b00fef714"

# Get data for the specified device.
device_data = GetDeviceData(api_token, server, device_id)
if device_data is not None:
    print("Device Data:")
    print(device_data)

# put /api/devices/{device.dev_eui}
def PutDevice(server, api_token, dev_eui, device_data):
    url = f"http://{server}/api/devices/{dev_eui}"
    auth_token = {"authorization": f"Bearer {api_token}"}

    try:
        response = requests.put(url, json=device_data, headers=auth_token)
        if response.status_code == 200:
            print("Dispositivo actualizado correctamente.")
        else:
            print(f"Error al actualizar el dispositivo. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar la solicitud PUT: {str(e)}")

dev_eui = "0000000000000001"
device_data = {
  "device": {
    "devEUI": "0000000000000001",
    "name": "0000000000000001",
    "applicationID": "1",
    "description": "Lo cree automaticamente",
    "deviceProfileID": "3363bcd9-6520-48c6-8d9d-845608aa5e57",
    "skipFCntCheck": True,
    "referenceAltitude": 0,
    "isDisabled": False,
    "tags": {},
    "variables": {}
  }
}

PutDevice(server, api_token, dev_eui, device_data)

# post /api/devices
def PostDevice(server, api_token, device_data):
    url = f"http://{server}/api/devices"
    auth_token = {"authorization": f"Bearer {api_token}"}

    try:
        response = requests.post(url, json=device_data, headers=auth_token)
        if response.status_code == 200:
            print("Dispositivo agregado correctamente.")
        else:
            print(f"Error al agregar el dispositivo. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar la solicitud POST: {str(e)}")

device_data = {
  "device": {
    "devEUI": "0000000000000002",
    "name": "0000000000000002",
    "applicationID": "1",
    "description": "Lo cree automaticamente",
    "deviceProfileID": "3363bcd9-6520-48c6-8d9d-845608aa5e57",
    "skipFCntCheck": True,
    "referenceAltitude": 0,
    "isDisabled": False,
    "tags": {},
    "variables": {}
  }
}

PostDevice(server, api_token, device_data)

# delete /api/devices/{dev_eui}
def DeleteDevice(server, api_token, dev_eui):
    url = f"http://{server}/api/devices/{dev_eui}"
    auth_token = {"authorization": f"Bearer {api_token}"}

    try:
        response = requests.delete(url, headers=auth_token)
        if response.status_code == 200:
            print("Dispositivo eliminado correctamente.")
        else:
            print(f"Error al eliminar el dispositivo. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar la solicitud DELETE: {str(e)}")

dev_eui = "0000000000000001"

DeleteDevice(server, api_token, dev_eui)

# get /api/devices/{dev_eui}/activation 
def GetDeviceActivation(api_token, server, device_id):
    url = f"http://{server}/api/devices/{device_id}/activation"
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    response = requests.get(url, headers=dict(auth_token))
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener las activaciones del dispositivo: {response.status_code}")
        return None

device_id = "0004a30b00fef714"

device_activations = GetDeviceActivation(api_token, server, device_id)

if device_activations:
    print("Device Activations::", device_activations)

# delete /api/devices/{dev_eui}/activation 
def DeleteDeviceActivation(api_token, server, dev_eui):
    url = f"http://{server}/api/devices/{dev_eui}/activation"
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    response = requests.delete(url, headers=dict(auth_token))
    
    if response.status_code == 200:
        print(f"Activación del dispositivo {dev_eui} eliminada con éxito.")
    else:
        print(f"Error al eliminar la activación del dispositivo: {response.status_code}")

dev_eui = "0000000000000001"

DeleteDeviceActivation(api_token, server, dev_eui)

# post /api/devices/{device_activation.dev_eui}/activate 
def PostDeviceActivation(api_token, server, dev_eui, activation_data):
    url = f"http://{server}/api/devices/{dev_eui}/activate"
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    response = requests.post(url, json=activation_data, headers=dict(auth_token))
    
    if response.status_code == 200:
        print("Activación del dispositivo exitosa.")
    else:
        print(f"Error al activar el dispositivo: {response.status_code}")

dev_eui = "0000000000000001"

activation_data = {
    "deviceActivation": {
        "aFCntDown": 0,
        "appSKey": "0b3f97455e1e0910952bdcd12f08e752",
        "devAddr": "00497fad",
        "devEUI": "0000000000000001",
        "fCntUp": 138,
        "fNwkSIntKey": "3f196e3d5e1bcfedd938292c409cf0bc",
        "nFCntDown": 0,
        "nwkSEncKey": "3f196e3d5e1bcfedd938292c409cf0bc",
        "sNwkSIntKey": "3f196e3d5e1bcfedd938292c409cf0bc"
    }
}

PostDeviceActivation(api_token, server, dev_eui, activation_data)

# get /api/devices/{dev_eui}/events 
def GetDeviceEvents(api_token, server, device_id):
    # Define the API endpoint to get events for a specific device.
    url = f"http://{server}/api/devices/{device_id}/events"

    # Define headers with authorization token.
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Make a GET request to the API endpoint.
    response = requests.get(url, headers=dict(auth_token))

    # Check if the request was successful.
    if response.status_code == 200:
        # Parse the response JSON.
        events = response.json()
        return events
    else:
        # Print error message if request failed.
        print(f"Failed to get device events: {response.text}")
        return None

device_id = "0004a30b00fef714"

# Get events for the specified device.
events = GetDeviceEvents(api_token, server, device_id)
if events is not None:
    for event in events:
        print(f"Event ID: {event['id']}, Type: {event['type']}, Timestamp: {event['timestamp']}, Data: {event['data']}")

# get /api/devices/{dev_eui}/frames 
def GetDeviceFrames(api_token, server, device_id):
    # Define the API endpoint to get frames for a specific device.
    url = f"http://{server}/api/devices/{device_id}/frames"

    # Define headers with authorization token.
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Make a GET request to the API endpoint.
    response = requests.get(url, headers=dict(auth_token))

    # Check if the request was successful.
    if response.status_code == 200:
        # Parse the response JSON.
        frames = response.json()
        return frames
    else:
        # Print error message if request failed.
        print(f"Failed to get frames: {response.text}")
        return None

device_id = "0004a30b00fef714"

# Get frames for the specified device.
frames = GetDeviceFrames(api_token, server, device_id)
if frames is not None:
    for frame in frames:
        print(f"Timestamp: {frame['timestamp']}, Data: {frame['data']}")

# post /api/devices/{dev_eui}/getRandomDevAddr
def GetRandomDevAddr(dev_eui, server, api_token):
    url = f"http://{server}/api/devices/{dev_eui}/getRandomDevAddr"
    auth_token = {"Authorization": f"Bearer {api_token}"}

    response = requests.post(url, headers=auth_token)

    if response.status_code == 200:
        random_dev_addr = response.json()
        print("Dirección de dispositivo aleatoria:")
        print(random_dev_addr)
    else:
        print("Error al obtener la dirección de dispositivo aleatoria:", response.status_code)

dev_eui = "0004a30b00fef714"  

GetRandomDevAddr(dev_eui, server, api_token)

# get /api/devices/{dev_eui}/stats
def GetDeviceStats():
    device_data = {
        "device_id": "0004a30b00fef714",
        "interval": "minute",
        "startTimestamp": "2024-05-07T10:35:02.358Z",  
        "endTimestamp": "2024-05-07T10:36:02.358Z",  
    }

    device_id = device_data["device_id"]
    interval = device_data["interval"]
    startTimestamp = device_data["startTimestamp"]
    endTimestamp = device_data["endTimestamp"]
    
    auth_token = {"Authorization": f"Bearer {api_token}"}

    try:
        url = f'http://{server}/api/devices/{device_id}/stats?interval={interval}&startTimestamp={startTimestamp}&endTimestamp={endTimestamp}'
        resp = requests.get(url, headers=auth_token)

        if resp.status_code == 200:
            device_stats = resp.json()
            print("Información de estadísticas del device dentro del intervalo de tiempo:")
            print(device_stats)
        else:
            print("Error al obtener las estadísticas del device. Código de estado:", resp.status_code)
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)

GetDeviceStats()

# get /api/devices/{dev_eui}/keys 
def GetDeviceKeys(api_token, server, device_id):
    url = f"http://{server}/api/devices/{device_id}/keys"
    auth_token = {"authorization": f"Bearer {api_token}"}
    
    response = requests.get(url, headers=dict(auth_token))
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get device keys: {response.status_code}")
        return None

device_id = "0004a30b00fef714"

device_keys = GetDeviceKeys(api_token, server, device_id)

if device_keys:
    print("Device Keys:", device_keys)

# post /api/devices/{device_keys.dev_eui}/keys
def PostDeviceKeys(server, api_token, device_id, keys):
    url = f"http://{server}/api/devices/{device_id}/keys"
    auth_token = {"authorization": f"Bearer {api_token}"}

    try:
        response = requests.post(url, json=keys, headers=auth_token)
        if response.status_code == 200:
            print("Claves del dispositivo actualizadas correctamente.")
        else:
            print(f"Error al actualizar las claves del dispositivo. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar la solicitud POST: {str(e)}")

device_id = "0000000000000001"
keys = {
  "deviceKeys": {
    "devEUI": "0000000000000001",
    "nwkKey": "00000000000000000004a30b00fef714",
    "appKey": "00000000000000000000000000000000",
    "genAppKey": ""
  }
}

PostDeviceKeys(server, api_token, device_id, keys)

# put /api/devices/{device_keys.dev_eui}/keys
def PutDeviceKeys(server, api_token, device_id, keys):
    url = f"http://{server}/api/devices/{device_id}/keys"
    auth_token = {"authorization": f"Bearer {api_token}"}

    try:
        response = requests.put(url, json=keys, headers=auth_token)
        if response.status_code == 200:
            print("Claves del dispositivo actualizadas correctamente.")
        else:
            print(f"Error al actualizar las claves del dispositivo. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar la solicitud PUT: {str(e)}")

device_id = "0000000000000001"
keys = {
  "deviceKeys": {
    "nwkKey": "00000000000000000004a30b00fef714",
    "appKey": "00000000000000000000000000000000",
    "genAppKey": ""
  }
}

PutDeviceKeys(server, api_token, device_id, keys)

# delete /api/devices/{dev_eui}/keys 
def DeleteDeviceKeys(api_token, server, dev_eui):
    url = f"http://{server}/api/devices/{dev_eui}/keys"
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    response = requests.delete(url, headers=dict(auth_token))
    
    if response.status_code == 200:
        print(f"Claves del dispositivo {dev_eui} eliminadas con éxito.")
    else:
        print(f"Error al eliminar las claves del dispositivo {dev_eui}. Código de estado: {response.status_code}")

dev_eui = "0000000000000001"
# key: 43 68 65 6d 69 6b 20 5a 61 72 61 67 6f 7a 61 20

DeleteDeviceKeys(api_token, server, dev_eui)