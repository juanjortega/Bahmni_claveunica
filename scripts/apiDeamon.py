import time
import mysql.connector
import requests
from dotenv import load_dotenv
import os

# Conexión a la base de datos MySQL

openmrsdb = mysql.connector.connect(
    host=os.getenv("openmrsip_var"),
    user=os.getenv("user_var"),
    password=os.getenv("password_var"),
    database=os.getenv("openmrs")
)


while True:
    openmrscursor = openmrsdb.cursor()
    openmrscursor.execute("select order_id from orders od where od.order_type_id=2 "
                          "and od.order_id not in (select odp.order_id  from orderPrescriptions odp "
                          "where odp.status='E')")
    openmrsResult = openmrscursor.fetchall()
    openmrsdb.commit();
    for resul in openmrsResult:
        try:
            stmtq ="insert into orderPrescriptions (order_id,prescriptor_id,status,date_created)values("+str(resul[0])+",'apiDaemon','E',CURDATE())";
            openmrscursor.execute(stmtq);
            openmrsdb.commit();
        except:
            True
    time.sleep(5)

