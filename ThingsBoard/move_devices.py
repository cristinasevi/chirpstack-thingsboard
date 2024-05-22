import requests

def obtener_token_de_acceso_thingsboard():
    # Endpoint de autenticación de ThingsBoard
    login_endpoint = "http://thingsboard.chemik.es/api/auth/login"

    # Datos de autenticación de ThingsBoard
    auth_data = {
        "username": "info@inartecnologias.es",
        "password": "Inar.2019"
    }

    try:
        # Realizar la solicitud de autenticación a ThingsBoard
        response = requests.post(login_endpoint, json=auth_data)

        # Verificar el código de estado de la respuesta
        if response.status_code == 200:
            # Extraer el token de acceso de la respuesta
            access_token = response.json().get("token")
            return access_token
        else:
            print(f"Error de autenticación en ThingsBoard. Código de estado: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print("Error al conectar con ThingsBoard para autenticación.")
        print(e)
        return None

def obtener_dispositivo_por_dev_eui(dev_eui, token_chirpstack):
    # Endpoint de ChirpStack para buscar un dispositivo por dev_eui
    chirpstack_endpoint = f"http://localhost:8080/api/devices/{dev_eui}"
    headers = {
        "Grpc-Metadata-Authorization": f"Bearer {token_chirpstack}"
    }

    try:
        # Realizar la solicitud para obtener información del dispositivo en ChirpStack
        response = requests.get(chirpstack_endpoint, headers=headers)
        
        # Verificar el código de estado de la respuesta
        if response.status_code == 200:
            # Retornar los datos del dispositivo
            return response.json()
        else:
            print(f"Error al obtener información del dispositivo en ChirpStack. Código de estado: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print("Error al conectar con ChirpStack.")
        print(e)
        return None

def enviar_datos_a_thingsboard(datos_dispositivo, cliente_id, dev_eui):
    # Obtener el token de acceso de ThingsBoard
    access_token_thingsboard = obtener_token_de_acceso_thingsboard()
    if access_token_thingsboard:
        # Endpoint de ThingsBoard para enviar datos del dispositivo
        thingsboard_endpoint = "http://thingsboard.chemik.es/api/device"
        headers = {
            "X-Authorization": f"Bearer {access_token_thingsboard}",
            "Content-Type": "application/json"
        }

        # Agregar el cliente_id a los datos del dispositivo
        datos_dispositivo["clientId"] = cliente_id

        # Verificar si el nombre del dispositivo está presente, si no, asignar uno por defecto
        if "name" not in datos_dispositivo:
            datos_dispositivo["name"] = dev_eui

        try:
            # Realizar la solicitud para enviar datos del dispositivo a ThingsBoard
            response = requests.post(thingsboard_endpoint, json=datos_dispositivo, headers=headers)
            
            # Verificar el código de estado de la respuesta
            if response.status_code == 200:
                print(f"Datos del dispositivo {datos_dispositivo['name']} enviados correctamente a ThingsBoard.")
            else:
                print(f"Error al enviar datos de los dispositivos a ThingsBoard. Código de estado: {response.status_code}")
                print(response.text)
        
        except Exception as e:
            print("Error al conectar con ThingsBoard.")
            print(e)

def procesar_dispositivos(dev_euis, cliente_id, token_chirpstack):
    for dev_eui in dev_euis:
        # Obtener los datos del dispositivo en ChirpStack
        datos_dispositivo = obtener_dispositivo_por_dev_eui(dev_eui, token_chirpstack)

        if datos_dispositivo:
            # Enviar los datos del dispositivo a ThingsBoard con el cliente ID
            enviar_datos_a_thingsboard(datos_dispositivo, cliente_id, dev_eui)

# Variables de prueba
dev_euis = ["0004a30b00f98b5c", "0004a30b00f986d5"]
token_chirpstack = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiZTc0NjBmNWUtNWNjMy00YWM3LWFkMWYtZjZlYTQ3NWYwMDlkIiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTcxNDk4Mjg0OSwic3ViIjoiYXBpX2tleSJ9.PhRDrQFKrhXWJyBkHAEyQuousmOPhCI5WOcNpK5hIbU"
cliente_id = "dc8383c0-f0d9-11ee-a9f5-675b85d8bd3b"

# Procesar los dispositivos
procesar_dispositivos(dev_euis, cliente_id, token_chirpstack)