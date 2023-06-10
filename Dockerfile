# Usa una imagen base con Python 3.9
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de código fuente y los requisitos al contenedor
COPY . /app

# Instala las dependencias del proyecto
RUN pip install -r requirements.txt

# Mueve el archivo .env al directorio de trabajo dentro del contenedor
RUN mv .env /app/.env

# Expone el puerto 5001 para la aplicación Flask
EXPOSE 5001

# Ejecuta el comando para iniciar la aplicación Flask
CMD ["python", "nombre_del_archivo.py"]
