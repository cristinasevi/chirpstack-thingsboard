import json
from pymodbus.client import ModbusTcpClient
from datetime import datetime
import openpyxl
from openpyxl import Workbook
import time

# Función para cargar la configuración desde un archivo JSON
def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error al cargar el archivo de configuración {file_path}: {e}")
        return {}

# Función para leer un registro específico
def read_register(client, address):
    try:
        result = client.read_input_registers(address, 1)
        if not result.isError():
            return result.registers[0]
        else:
            print(f"Error al leer el registro en la dirección {address}")
            return None
    except Exception as e:
        print(f"Excepción al leer el registro {address}: {e}")
        return None

# Configuración del servidor Modbus
ip_modbus_server = "{{modbus_server_ip}}"
modbus_ports = [506]

# Cargar la configuración desde el archivo JSON
config_file = 'config.json'
config = load_config(config_file)

# Filtrar las claves no deseadas
excluded_keys = {'key1', 'key2', 'key3', 'key4'}

# Crear lista de dispositivos excluyendo las claves no deseadas
devices = [device_id for device_id in config.keys() if device_id not in excluded_keys]

# Crear un nuevo archivo Excel
wb = Workbook()
ws = wb.active
ws.title = 'Channels'

# Escribir encabezados
headers = ['Datetime'] + devices
ws.append(headers)

# Variable para rastrear si la conexión fue exitosa
connection_successful = False

# Intentar conectar al servidor Modbus en los puertos especificados
for port in modbus_ports:
    client = ModbusTcpClient(ip_modbus_server, port=port)
    
    # Conexión al servidor
    if client.connect():
        print(f"Conectado al servidor Modbus en {ip_modbus_server}:{port}")
        connection_successful = True
        break
    else:
        print(f"Fallo al conectar al servidor Modbus en {ip_modbus_server}:{port}")

# Si no se pudo conectar a ningún puerto
if not connection_successful:
    print("No se pudo conectar a ningún servidor Modbus.")
else:
    # Bucle infinito para leer valores cada minuto
    try:
        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_row_channels = [timestamp]
            
            for device_id, device_config in config.items():
                if device_id in excluded_keys:
                    continue
                if isinstance(device_config, dict) and 'addresses' in device_config and isinstance(device_config['addresses'], dict):
                    addresses = device_config['addresses']
                    
                    channels = []
                    for name, address in addresses.items():
                        if name.startswith("channel"):  # Procesar solo los canales
                            value = read_register(client, address)
                            if value is not None:
                                channels.append(value / 10)  # Dividir por 10 para los canales
                            else:
                                channels.append(None)

                    if channels:
                        # Convertir la lista de canales a una cadena
                        new_row_channels.append(str(channels))
                    else:
                        new_row_channels.append(None)
                else:
                    print(f"Advertencia: La configuración para el dispositivo {device_id} no es válida.")
                    new_row_channels.append(None)
            
            # Añadir la nueva fila al archivo Excel
            ws.append(new_row_channels)
            print(f"Datos de channels registrados para {timestamp}")

            # Guardar el archivo Excel
            wb.save('modbus_channels_data.xlsx')

            # Esperar 60 segundos antes de la próxima lectura
            time.sleep(60)
    except KeyboardInterrupt:
        # Cerrar la conexión Modbus
        client.close()
        print("Ejecución interrumpida. Conexión cerrada.")