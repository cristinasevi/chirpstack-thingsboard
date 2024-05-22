import grpc
from chirpstack_api.as_pb.external import api
from datetime import datetime
import time
import openpyxl
import os
import configparser

import requests 

import pandas as pd

server = "localhost:8090"
api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjaGlycHN0YWNrIiwiaXNzIjoiY2hpcnBzdGFjayIsInN1YiI6IjJjYmZjOWIxLWIzZDgtNDU3NC1hMTJjLWVmNzhiYWIwZTAyOCIsInR5cCI6ImtleSJ9.4Qzq6v_KcOvKEgXzewMNbRPS4uxE-pwcGKNjemDsRrk"
Com_Count = 0
last_checked_day = None
Device_List = []
Gateway_List = []

# Leer configuraciones desde config.ini
config = configparser.ConfigParser()
config.read('config.ini')

Comm_Threshold = config['DEFAULT'].getint('Comm_Threshold', 300)  # Convertir a entero, usar 300 por defecto si no se encuentra
Log_Rate = config['DEFAULT'].getint('Log_Rate', 60)  # Convertir a entero, usar 60 por defecto si no se encuentra
Plant_Name = config['DEFAULT'].get('Plant_Name', 'Erla')  # Si no se encuentra, usar 'Erla' por defecto

def PostDeviceActivation(api_token, server, dev_eui, activation_data):
    url = f"http://{server}/api/devices/{dev_eui}/activate"
    headers = {
        "accept": "application/json",
        "Grpc-Metadata-Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=activation_data, headers=dict(headers))
    
    if response.status_code == 200:
        print(f"Activación del dispositivo {dev_eui} exitosa.")
    else:
        print(f"Error al activar el dispositivo {dev_eui}. Código de error: {response.status_code}")

def PostDeviceActivationXLSX(api_token, server, xlsx_file, start_row, end_row):
    try:
        data = pd.read_excel(xlsx_file)
        data = data.astype(str)  # Convertir todas las columnas a cadenas
        for row_index, row in data.iterrows():
            if start_row <= row_index + 1 <= end_row:
                try:
                    if len(row) >=9:
                        dev_eui = row.iloc[2][3:19]  # Obtener los EUI de la tercera columna del cuarto al decimonoveno caracter
                        activation_data = {
                            "deviceActivation": {
                                "aFCntDown": 0,  
                                "appSKey": "00000000000000000000000000000000",
                                "devAddr": row.iloc[4][3:11],
                                "devEUI": row.iloc[2][3:19],
                                "fCntUp": 138, 
                                "fNwkSIntKey": row.iloc[5][3:35],
                                "nFCntDown": 0,  
                                "nwkSEncKey": row.iloc[7][3:35],
                                "sNwkSIntKey": row.iloc[6][3:35]
                            }
                        }
                        PostDeviceActivation(api_token, server, dev_eui, activation_data)
                    else:
                        print(f"Error: No hay suficientes columnas en la fila {row_index}.")
                except IndexError as e:
                    print(f"Error en la fila {row_index + 1}: {e}")
                    continue
                print(f"Respuesta de activación para el dispositivo {dev_eui}: {activation_data}")
    except FileNotFoundError:
        print(f"El archivo {xlsx_file} no se encontró.")

xlsx_file = "prueba.xlsx"
start_row = 569
end_row = 600

PostDeviceActivationXLSX(api_token, server, xlsx_file, start_row, end_row)
