# Establece la imagen base
FROM python:3.9

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos requeridos al directorio de trabajo
COPY . /app

# Instala las dependencias
RUN pip install -r requirements.txt

# Expone cualquier puerto necesario para tu aplicación
EXPOSE 81

# Establece las variables de entorno del archivo .env
ENV PYTHONPATH "${PYTHONPATH}:/app"  # Agregar cualquier ruta adicional necesaria
ENV DOTENV_PATH "/app/.env"

# Ejecuta los programas en segundo plano cuando se inicie el contenedor
CMD ["bash", "-c", "python apiDeamon.py & python apiRetoken.py & python mailsender.py"]
