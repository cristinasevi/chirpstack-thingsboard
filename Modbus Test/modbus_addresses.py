from pymodbus.client import ModbusTcpClient

# Configuración del servidor Modbus
ip_modbus_server = "{{modbus_server_ip}}"
modbus_ports = [506]

# Direcciones de los registros
addresses = {
    "channel1": 98,
    "channel2": 97,
    "channel3": 96,
    "channel4": 319,
    "rssi": 5068,
    "timestamp": 6068,
    "status": 7068
}

# Variable para rastrear si la conexión fue exitosa
connection_successful = False

# Intentar conectar al servidor Modbus en los puertos especificados
for port in modbus_ports:
    client = ModbusTcpClient(ip_modbus_server, port=port)
    
    # Conexión al servidor
    if client.connect():
        print(f"Conectado al servidor Modbus en {ip_modbus_server}:{port}")
        connection_successful = True

        # Leer registros específicos
        def read_register(address):
            result = client.read_input_registers(address, 1)
            if not result.isError():
                return result.registers[0]
            else:
                print(f"Error al leer el registro en la dirección {address}")
                return None
        
        # Leer y procesar los valores de los canales
        channel1 = read_register(addresses["channel1"])
        channel2 = read_register(addresses["channel2"])
        channel3 = read_register(addresses["channel3"])
        channel4 = read_register(addresses["channel4"])
        
        # Leer otros valores sin dividir
        rssi = read_register(addresses["rssi"])
        timestamp = read_register(addresses["timestamp"])
        status = read_register(addresses["status"])
        
        # Convertir rssi a un entero con signo de 16 bits si es necesario
        if rssi is not None:
            rssi = rssi if rssi < 0x8000 else rssi - 0x10000
        
        # Mostrar los valores leídos
        print(f"Channel 1: {channel1 / 10 if channel1 is not None else 'NaN'}")
        print(f"Channel 2: {channel2 / 10 if channel2 is not None else 'NaN'}")
        print(f"Channel 3: {channel3 / 10 if channel3 is not None else 'NaN'}")
        print(f"Channel 4: {channel4 / 10 if channel4 is not None else 'NaN'}")
        print(f"RSSI: {rssi if rssi is not None else 'NaN'}")
        print(f"Timestamp: {timestamp / 10 if timestamp is not None else 'NaN'}")
        print(f"Status: {status if status is not None else 'NaN'}")  
        
        # Cerrar la conexión
        client.close()
        break
    else:
        print(f"Fallo al conectar al servidor Modbus en {ip_modbus_server}:{port}")

# Si no se pudo conectar a ningún puerto
if not connection_successful:
    print("No se pudo conectar a ningún servidor Modbus.")