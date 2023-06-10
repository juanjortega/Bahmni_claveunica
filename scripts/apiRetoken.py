import requests
import mysql.connector
from flask import Flask, request, jsonify,redirect
app = Flask(__name__)
teledb = mysql.connector.connect(
    host="10.100.100.70",
    user="re_user",
    password="bU1&GICI52n",
    database="openmrs"
);
@app.route('/claveunica',methods=['GET'])
def tokenizer():
    try:
        telecursor = teledb.cursor()
        content = request.args;
        codigo = content.get('code');
        resp=requests.post("https://apiqa-receta.minsal.cl/oauth/token",
                           data={"Content-Type":"application/x-www-form-urlencoded",
                                 "grant_type":"authorization_code",
                                 "client_id":"42a6d39b-b3af-4b55-b801-7fa135eaec1f",
                                 "client_secret":"09ca9aaf-3a25-4b0d-a11c-6bce84207a4b",
                                 "redirect_uri":"http://10.100.100.80/claveunica",
                                 "code": codigo})
        print("1")
        resp_dict = resp.json()
        mecall=requests.get("https://apiqa-receta.minsal.cl/me",
                            headers={"Authorization":"Bearer "+str(resp_dict.get('access_token'))});
        resp_me = mecall.json()
        print("1")
        stmtdel="delete from token_users where run_medico="+str(resp_me.get('run'));
        telecursor.execute(stmtdel);
        teledb.commit();
        stmtq ="insert into token_users (token,refresh_token,run_medico)" \
               +"values('"+str(resp_dict.get("access_token")) \
               +"','"+str(resp_dict.get('refresh_token')) \
               +"','"+str(resp_me.get('run'))+"')";
        print(stmtq)
        print("1")
        telecursor.execute(stmtq);
        teledb.commit();
        if resp.status_code==200 :
            return redirect("http://10.100.100.70:80/bahmni/home", code=302)
        response = requests.get('http://10.100.100.70:80/bahmni/home', verify=False)
    except:
        print('Se produjo una falla al invocar clave unica');
app.run(host='0.0.0.0', port=5001);