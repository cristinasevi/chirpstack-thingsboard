import json
from pymodbus.client import ModbusTcpClient
import math

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

# Función para convertir un valor a un entero con signo de 16 bits
def convert_to_signed_16bit(value):
    if value >= 0x8000:
        return value - 0x10000
    else:
        return value

# Función para verificar y ajustar el valor leído
def process_value(name, value):
    if name == "rssi":
        return convert_to_signed_16bit(value)  # No dividir por 10 para rssi
    elif name == "status":
        return value  # No dividir por 10 para status
    else:
        value = value / 10  # Dividir por 10 para los otros canales
        # Verificar si el valor está dentro de un rango razonable
        if value < 1000:  # Ajustar según el rango esperado de tus datos
            return value
        else:
            return float('nan')  # Devolver NaN si el valor es inesperadamente alto

# Función para escribir los valores en un archivo de texto
def write_to_txt(data, file_path):
    try:
        with open(file_path, 'w') as file:
            for device_id, values in data.items():
                file.write(f"Valores para el dispositivo {device_id}:\n")
                for name, value in values.items():
                    file.write(f"{name}: {value}\n")
                file.write("\n")
        print(f"Datos guardados exitosamente en {file_path}")
    except Exception as e:
        print(f"Error al escribir en el archivo {file_path}: {e}")

# Configuración del servidor Modbus
ip_modbus_server = "{{modbus_server_ip}}"
modbus_ports = [506]

# Cargar la configuración desde el archivo JSON
config_file = 'config.json'
config = load_config(config_file)

# Variable para almacenar los valores leídos
data_to_write = {}

# Variable para rastrear si la conexión fue exitosa
connection_successful = False

# Intentar conectar al servidor Modbus en los puertos especificados
for port in modbus_ports:
    client = ModbusTcpClient(ip_modbus_server, port=port)
    
    # Conexión al servidor
    if client.connect():
        print(f"Conectado al servidor Modbus en {ip_modbus_server}:{port}")
        connection_successful = True

        # Iterar sobre la configuración y leer los registros
        for device_id, device_config in config.items():
            if isinstance(device_config, dict) and 'addresses' in device_config and isinstance(device_config['addresses'], dict):
                addresses = device_config['addresses']
                device_values = {}

                for name, address in addresses.items():
                    value = read_register(client, address)
                    if value is not None:
                        processed_value = process_value(name, value)
                        if not math.isnan(processed_value):
                            device_values[name] = processed_value
                        else:
                            device_values[name] = "NaN"
                    else:
                        device_values[name] = "No se pudo leer"

                # Almacenar los valores del dispositivo en el diccionario
                data_to_write[device_id] = device_values

                print(f"\nValores para el dispositivo {device_id}:")
                for name, value in device_values.items():
                    print(f"{name}: {value}")
            else:
                print(f"Advertencia: La configuración para el dispositivo {device_id} no es válida.")

        # Cerrar la conexión
        client.close()
        break
    else:
        print(f"Fallo al conectar al servidor Modbus en {ip_modbus_server}:{port}")

# Si no se pudo conectar a ningún puerto
if not connection_successful:
    print("No se pudo conectar a ningún servidor Modbus.")

# Guardar los valores en un archivo de texto
write_to_txt(data_to_write, 'valores_modbus.txt')