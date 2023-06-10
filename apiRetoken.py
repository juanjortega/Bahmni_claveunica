import requests
import mysql.connector
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv
import os

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la aplicación Flask
app = Flask(__name__)

# Conexión a la base de datos MySQL
teledb = mysql.connector.connect(
    host=os.getenv("openmrsip_var"),
    user=os.getenv("user_var"),
    password=os.getenv("password_var"),
    database=os.getenv("openmrs")
)

# Ruta para el endpoint '/claveunica' con método GET
@app.route('/claveunica', methods=['GET'])
def tokenizer():
    try:
        telecursor = teledb.cursor()

        # Obtener el código de la consulta GET
        content = request.args
        codigo = content.get('code')

        # Enviar una solicitud POST para obtener el token de acceso
        resp = requests.post(
            "https://apiqa-receta.minsal.cl/oauth/token",
            data={
                "Content-Type": "application/x-www-form-urlencoded",
                "grant_type": "authorization_code",
                "client_id": os.getenv("client_id_var"),
                "client_secret": os.getenv("client_secret_var"),
                "redirect_uri": 'http://' + os.getenv("bahmni-caveunica_var") + "/claveunica",
                "code": codigo
            }
        )
        print("1")
        resp_dict = resp.json()

        # Obtener información del usuario autenticado usando el token de acceso
        mecall = requests.get(
            "https://apiqa-receta.minsal.cl/me",
            headers={"Authorization": "Bearer " + str(resp_dict.get('access_token'))}
        )
        resp_me = mecall.json()
        print("1")
        # Eliminar el token de usuario existente asociado al RUN del usuario autenticado
        stmtdel = "delete from token_users where run_medico=" + str(resp_me.get('run'))
        telecursor.execute(stmtdel)
        teledb.commit()

        # Insertar el nuevo token de usuario en la base de datos
        stmtq = "insert into token_users (token,refresh_token,run_medico)" \
            + "values('" + str(resp_dict.get("access_token")) \
            + "','" + str(resp_dict.get('refresh_token')) \
            + "','" + str(resp_me.get('run')) + "')"
        print(stmtq)
        print("1")
        telecursor.execute(stmtq)
        teledb.commit()

        # Redirigir al usuario a la página de inicio después de la autenticación exitosa
        if resp.status_code == 200:
            return redirect('http://' + os.getenv("urlhome_var") + ':80/bahmni/home', code=302)

        # Enviar una solicitud GET a una URL de inicio alternativa si la autenticación no fue exitosa
        response = requests.get(('http://' + os.getenv("urlhome_var") + ':80/bahmni/home'), verify=False)

    except Exception as e:
        print('Se produjo una falla al invocar clave unica:', str(e))

# Iniciar la aplicación Flask en el host '0.0.0.0' en el puerto 5001
app.run(host='0.0.0.0', port=5001)
