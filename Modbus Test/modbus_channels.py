from pymodbus.client import ModbusTcpClient

# Configuración del servidor Modbus
ip_modbus_server = "{{modbus_server_ip}}"
modbus_ports = [506]

# Variable para rastrear si la conexión fue exitosa
connection_successful = False

# Intentar conectar al servidor Modbus en los puertos especificados
for port in modbus_ports:
    client = ModbusTcpClient(ip_modbus_server, port=port)
    
    # Conexión al servidor
    if client.connect():
        print(f"Conectado al servidor Modbus en {ip_modbus_server}:{port}")
        connection_successful = True

        # Leer registros específicos (por ejemplo, Input Registers en el rango 0-9)
        start_address = 96
        count = 3  # Número de registros a leer
        result = client.read_input_registers(start_address, count)

        if not result.isError():
            # Acceso a los datos leídos
            registers = result.registers
            print("Registros leídos: ", registers)

            # Acceso a datos específicos
            if len(registers) >= 3:
                channel1 = registers[2] / 10
                channel2 = registers[1] / 10
                channel3 = registers[0] / 10

                print(f"Channel 1: {channel1}")
                print(f"Channel 2: {channel2}")
                print(f"Channel 3: {channel3}")
            else:
                print("No se leyeron suficientes registros para los canales esperados.")
        else:
            print("Error al leer los registros")

        # Cerrar la conexión
        client.close()
        break
    else:
        print(f"Fallo al conectar al servidor Modbus en {ip_modbus_server}:{port}")

# Si no se pudo conectar a ningún puerto
if not connection_successful:
    print("No se pudo conectar a ningún servidor Modbus.")