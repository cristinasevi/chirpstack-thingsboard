import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Datos del remitente y destinatario
remitente = '{{correo_electronico1}}'
password = '{{oauth2Response.access_token}}'
destinatario = '{{correo_electronico2}}'

# Crear el objeto del mensaje
mensaje = MIMEMultipart()
mensaje['From'] = remitente
mensaje['To'] = destinatario
mensaje['Subject'] = 'Correo con archivo adjunto'

# Cuerpo del mensaje
cuerpo_mensaje = 'Adjunto tienes el archivo que solicitaste.'
mensaje.attach(MIMEText(cuerpo_mensaje, 'plain'))

# Archivo a adjuntar
nombre_archivo = 'archivo.xlsx'
ruta_archivo = '/home/ruta_del_archivo/archivo.xlsx'  # Modificar con la ruta correcta

# Abrir el archivo en modo binario
archivo_adjunto = open(ruta_archivo, 'rb')

# Crear el objeto MIME base
objeto_adjunto = MIMEBase('application', 'octet-stream')
objeto_adjunto.set_payload(archivo_adjunto.read())
archivo_adjunto.close()

# Codificar el objeto en base64
encoders.encode_base64(objeto_adjunto)

# Establecer las cabeceras del archivo adjunto
objeto_adjunto.add_header('Content-Disposition', f'attachment; filename= {nombre_archivo}')

# Adjuntar el archivo al mensaje
mensaje.attach(objeto_adjunto)

# Iniciar sesión en el servidor SMTP
servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)
servidor_smtp.starttls()
servidor_smtp.login(remitente, password)

# Enviar el mensaje
texto_mensaje = mensaje.as_string()
servidor_smtp.sendmail(remitente, destinatario, texto_mensaje)

# Cerrar la conexión SMTP
servidor_smtp.quit()

print('Correo enviado correctamente con el archivo adjunto.')