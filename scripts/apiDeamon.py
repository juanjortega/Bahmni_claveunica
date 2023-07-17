# Importar módulos

# Módulo para manejar el tiempo
import time

# Módulo para la conexión a la base de datos MySQL
import mysql.connector

# Módulo para realizar solicitudes HTTP
import requests

# Módulo para cargar variables de entorno desde un archivo .env
from dotenv import load_dotenv

# Módulo para acceder a funciones del sistema operativo
import os

# Conexión a la base de datos MySQL

# Establecer la conexión con la base de datos MySQL utilizando los valores de las variables de entorno

openmrsdb = mysql.connector.connect(
    host=os.getenv("openmrsip_var"),
    user=os.getenv("user_var"),
    password=os.getenv("password_var"),
    database=os.getenv("openmrs")
)


while True:
    # Crear un cursor para ejecutar consultas en la base de datos
    openmrscursor = openmrsdb.cursor()
    
    # Ejecutar una consulta SQL para obtener los valores de order_id de la tabla orders
    # Filtrar por order_type_id=2 y excluir los order_id que ya existen en la tabla orderPrescriptions con un estado 'E' 
    openmrscursor.execute("select order_id from orders od where od.order_type_id=2 "
                          "and od.order_id not in (select odp.order_id  from orderPrescriptions odp "
                          "where odp.status='E')")

    # Obtener todos los resultados de la consulta
    openmrsResult = openmrscursor.fetchall()
    
    # Confirmar los cambios en la base de datos
    openmrsdb.commit();
    
    # Iterar sobre cada resultado obtenido
    for resul in openmrsResult:
        try:
            # Construir una sentencia SQL para insertar un nuevo registro en la tabla orderPrescriptions
            # con el order_id, un prescriptor_id de 'apiDaemon', un estado 'E' y la fecha actual
            stmtq ="insert into orderPrescriptions (order_id,prescriptor_id,status,date_created)values("+str(resul[0])+",'apiDaemon','E',CURDATE())";

            # Ejecutar la sentencia SQL
            openmrscursor.execute(stmtq);

            # Confirmar los cambios en la base de datos
            openmrsdb.commit();
        except:
            True
            
    # Pausar la ejecución durante 5 segundos
    time.sleep(5)

