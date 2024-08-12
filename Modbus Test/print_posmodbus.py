import pandas as pd

# Cargar el archivo Excel
file_path = '/home/ruta_del_archivo/archivo.xlsx'
df = pd.read_excel(file_path)

# Extraer los valores de los canales (columnas 6 a 9) y los valores RSSI (columna 10)
channels = df.iloc[:, 5:9].values
rssi_values = df.iloc[:, 9].values

# Crear un array con los datos extraídos
data = {
    'channels': channels,
    'rssi': rssi_values
}

print(data)