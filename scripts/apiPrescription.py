import json
import time

from flask import Flask, request, jsonify
import mysql.connector
import requests
app = Flask(__name__)
from nanoid import generate
import logging
from email.message import EmailMessage
import smtplib

openmrsdb = mysql.connector.connect(
    host=os.getenv("openmrsip_var"),
    user=os.getenv("user_var"),
    password=os.getenv("password_var"),
    database=os.getenv("openmrs")
);
easydb = mysql.connector.connect(
    host=os.getenv("easyip_var"),
    user=os.getenv("easyuser_var"),
    password=os.getenv("easypassword_var"),
    database=os.getenv("easyappdb")
);
eternal=1;
while eternal < 2:
    openmrsonecursor = openmrsdb.cursor()
    openmrsonecursor.execute("select order_id from orderPrescriptions op where op.status='E'")
    openmrsoneResult = openmrsonecursor.fetchall()
    openmrsdb.commit();
    for resul in openmrsoneResult:
        openmrscursor = openmrsdb.cursor()
        stmtPres="select o.order_id,o.`encounter_id`,\nprv.`uuid` idMedico,\nu.`username` username_medico, " \
                 "\npname.`family_name` apellido_medico,\npname.`given_name`nombre_medico,piden.`identifier` " \
                 "run_paciente,\ndor.`drug_inventory_id` drugId,\n(select dug.name from drug dug where dug.drug_id=dor.`drug_inventory_id`) medicamento," \
                 "\ndor.dose_units doseId,\ndor.dose `dose`,\n(select name from concept_name where concept_id= dor.dose_units and concept_name_type='FULLY_SPECIFIED') doseUnitDisplay," \
                 "\ndor.`frequency` frequencyId," \
                 "\n(select name from concept_name cn,order_frequency of where cn.concept_id= of.`concept_id` and concept_name_type='FULLY_SPECIFIED' and of.`order_frequency_id`=dor.`frequency`) frequenciDysplay," \
                 "\ndor.duration_units periodId," \
                 "\ndor.duration period," \
                 "\n(select name from concept_name where concept_id= dor.duration_units and concept_name_type='FULLY_SPECIFIED') periodDisplay," \
                 "\ndor.route routeId," \
                 "\n(select name from concept_name where concept_id= dor.route and concept_name_type='FULLY_SPECIFIED') routeDisplay" \
                 "\n\nfrom orders o , " \
                 "\ndrug_order dor,\nprovider prv,\nperson_name pname,\nusers u,\npatient_identifier piden\n" \
                 "where o.order_type_id=2\n" \
                 "and o.`order_id`=dor.`order_id`\n" \
                 "and o.`orderer`=prv.`provider_id`\n" \
                 "and prv.`person_id`=pname.`person_id`\n" \
                 "and prv.`person_id`=u.`person_id`\n" \
                 "and o.`patient_id`=piden.`patient_id`\n" \
                 "and piden.identifier_type = 4\n" \
                 "and o.`order_id`="+str(resul[0])+"\n" \
                                                   "order by o.`encounter_id`;\n"
        print (stmtPres)
        openmrscursor.execute(stmtPres);
        openmrsResult = openmrscursor.fetchall()
        openmrsdb.commit();
        runmedico="555555555"
        for resul in openmrsResult:
            idMedico=str(resul[2])
            easycursor = easydb.cursor()
            easycursor.execute("select ndocumento,email from ea_users op  where service_uuid='"+str(idMedico)+"'")
            easyResult = easycursor.fetchall()
            easydb.commit();
            for easyresul in easyResult:
                runmedico=str(easyresul[0]).replace('-' , '')
                print("from query:::: "+runmedico)
                destinatario=str(easyresul[1])
            route=str(resul[17]) #routeId
            routeDisplay=str(resul[18]) #routeDisplay
            period=str(resul[15]) #period
            frequency=str(resul[12])#frequency
            periodUnit=str(resul[16]) #periodDisplay
            medicationDisplay=str(resul[8]) #medicamento
            medicationId=str(resul[7]) #drugId
            methodCode="123456"
            methodDisplay="por la de tucan"
            doseUnit=str(resul[10]) #dose
            doseValue=str(resul[11]) #doseUnitDisplay
            runPaciente =str(resul[6]) #run_paciente


        tokencursor = openmrsdb.cursor()
        tokencursor.execute("select token,refresh_token,CURDATE() from token_users where run_medico='"+runmedico+"'")
        teleResult = tokencursor.fetchall()
        openmrsdb.commit();
        for resul in teleResult:
            # Refresh Token /*
            reftoken=resul[1];
            print (reftoken)
            resp=requests.post("https://apiqa-receta.minsal.cl/oauth/token",
                data={"Content-Type":"application/x-www-form-urlencoded",
                      "grant_type":"refresh_token",
                      "client_id":"42a6d39b-b3af-4b55-b801-7fa135eaec1f",
                      "client_secret":"09ca9aaf-3a25-4b0d-a11c-6bce84207a4b",
                     "refresh_token":reftoken
                      })
            resp_dict = resp.json()
            tokencursor = openmrsdb.cursor()
            stmtup="UPDATE token_users SET token='"+str(resp_dict.get("access_token"))+"', refresh_token='"+str(resp_dict.get("refresh_token"))+"' WHERE refresh_token='"+reftoken+"'"
            tokencursor.execute(stmtup);
            openmrsdb.commit();
            #presctoken=resul[0];
            presctoken=str(resp_dict.get("access_token"))
            print (presctoken)
            # Refresh Token */
            fechaPresc=str(resul[2]);
            nanonumber =generate('1234567890abcdef', 20);
            #runpaciente=runPaciente.replace(".", '') #Liberar en version definitiva
            #print(runpaciente)
            runpaciente ="20107589-0" #comentar en version definitiva
            try:
                resppatient=requests.get("https://apiqa-receta.minsal.cl/v2/Patient?identifier.value="+runpaciente+"&identifier.type.coding.code=NNCHL&identifier.type.extension.coding.code=152",
                                         headers={"Authorization":"Bearer "+presctoken});
                resp_pat = resppatient.json();
                print (str(resppatient.status_code))
                personid=resp_pat.get('id');
                fullnamelist=str(resp_pat.get('name'))
                fullsch=fullnamelist.replace('[', '')
                fullsch=fullsch.replace(']', '')
                fullsch=fullsch.replace("'", '"')
                person_dict = json.loads(fullsch)
                fullnamepatient = person_dict['given']+' '+person_dict['family']
                respmedic=requests.get("https://apiqa-receta.minsal.cl/v2/Patient?identifier.value="+runmedico+"&identifier.type.coding.code=NNCHL&identifier.type.extension.coding.code=152",
                                       headers={"Authorization":"Bearer "+presctoken});
                resp_medic = respmedic.json();
                medid=resp_medic.get('id');
                fullnamemedlist=str(resp_medic.get('name'))
                fullmedsch=fullnamemedlist.replace('[', '')
                fullmedsch=fullmedsch.replace(']', '')
                fullmedsch=fullmedsch.replace("'", '"')
                med_dict = json.loads(fullmedsch)
                fullnamemed = med_dict['given']+' '+med_dict['family']
                medrequ='{'
                medrequ=medrequ+'"resourceType": "RequestGroup",'
                medrequ=medrequ+'"contained":['
                medrequ=medrequ+'{'
                medrequ=medrequ+'"id": "'+str(nanonumber)+'",'
                medrequ=medrequ+'"note": ['
                medrequ=medrequ+'{'
                medrequ=medrequ+'"text": "Cada 4 horas consumir un chicle o cuando sienta la necesidad de fumar"'
                medrequ=medrequ+'}'
                medrequ=medrequ+'],'
                medrequ=medrequ+'"intent": "order",'
                medrequ=medrequ+'"status": "active",'
                medrequ=medrequ+'"subject": {'
                medrequ=medrequ+'"display": "'+fullnamepatient+'",'
                medrequ=medrequ+'"reference": "https://api.receta.minsal.asimov.cl/v2/Patient/'+str(personid)+'"'
                medrequ=medrequ+'},'
                medrequ=medrequ+'"category": ['
                medrequ=medrequ+'{'
                medrequ=medrequ+'"coding": ['
                medrequ=medrequ+'{'
                medrequ=medrequ+'"code": "community"'
                medrequ=medrequ+'}'
                medrequ=medrequ+']'
                medrequ=medrequ+'}'
                medrequ=medrequ+'],'
                medrequ=medrequ+'"requester": {'
                medrequ=medrequ+'"display": "'+fullnamemed+'",'
                medrequ=medrequ+'"reference": "https://api.receta.minsal.asimov.cl/v2/Practitioner/'+str(medid)+'"'
                medrequ=medrequ+'},'
                medrequ=medrequ+'"authoredOn": "'+str(fechaPresc)+'",'
                medrequ=medrequ+'"resourceType": "MedicationRequest",'
                medrequ=medrequ+'"groupIdentifier": {'
                medrequ=medrequ+'"value": "'+str(nanonumber)+'"'
                medrequ=medrequ+'},'
                medrequ=medrequ+'"dosageInstruction": ['
                medrequ=medrequ+'{'
                medrequ=medrequ+'"route": {'
                medrequ=medrequ+'"coding": ['
                medrequ=medrequ+'{'
                medrequ=medrequ+'"code": "'+str(route)+'",'
                medrequ=medrequ+'"system": "http://snomed.info/sct",'
                medrequ=medrequ+'"display": "'+routeDisplay+'"'
                medrequ=medrequ+'}'
                medrequ=medrequ+']'
                medrequ=medrequ+'},'
                medrequ=medrequ+'"method": {'
                medrequ=medrequ+'"coding": ['
                medrequ=medrequ+'{'
                medrequ=medrequ+'"code": "'+str(methodCode)+'",'
                medrequ=medrequ+'"system": "http://snomed.info/sct",'
                medrequ=medrequ+'"display": "'+methodDisplay+'"'
                medrequ=medrequ+'}'
                medrequ=medrequ+']'
                medrequ=medrequ+'},'
                medrequ=medrequ+'"timing": {'
                medrequ=medrequ+'"repeat": {'
                medrequ=medrequ+'"period": "'+str(period)+'",'
                medrequ=medrequ+'"frequency": "'+str(frequency)+'",'
                medrequ=medrequ+'"periodUnit": "'+str(periodUnit)+'",'
                medrequ=medrequ+'"boundsDuration": {'
                medrequ=medrequ+'"value": 0'
                medrequ=medrequ+'}'
                medrequ=medrequ+'}'
                medrequ=medrequ+'},'
                medrequ=medrequ+'"doseAndRate": ['
                medrequ=medrequ+'{'
                medrequ=medrequ+'"doseQuantity": {'
                medrequ=medrequ+'"unit": "'+doseUnit+'",'
                medrequ=medrequ+'"value": "'+str(doseValue)+'"'
                medrequ=medrequ+'}'
                medrequ=medrequ+'}'
                medrequ=medrequ+']'
                medrequ=medrequ+'}'
                medrequ=medrequ+'],'
                medrequ=medrequ+'"courseOfTherapyType": {'
                medrequ=medrequ+'"coding": ['
                medrequ=medrequ+'{'
                medrequ=medrequ+'"code": "acute",'
                medrequ=medrequ+'"system": "https://www.hl7.org/fhir/valueset-medicationrequest-course-of-therapy.html",'
                medrequ=medrequ+'"display": "agudo"'
                medrequ=medrequ+'}'
                medrequ=medrequ+']'
                medrequ=medrequ+'},'
                medrequ=medrequ+'"medicationReference": {'
                medrequ=medrequ+'"display": "'+medicationDisplay+'",'
                medrequ=medrequ+'"reference": "https://api.receta.minsal.asimov.cl/v2/medication/'+str(medicationId)+'"'
                medrequ=medrequ+'}'
                medrequ=medrequ+' }'
                medrequ=medrequ+'],'
                medrequ=medrequ+'"groupIdentifier": {'
                medrequ=medrequ+'"value": "'+str(nanonumber)+'"'
                medrequ=medrequ+'},'
                medrequ=medrequ+'"status": "completed",'
                medrequ=medrequ+'"intent": "order",'
                medrequ=medrequ+'"subject": {'
                medrequ=medrequ+'"reference": "https://api.receta.minsal.asimov.cl/v2/Patient/'+str(personid)+'",'
                medrequ=medrequ+'"display": "'+fullnamepatient+'"'
                medrequ=medrequ+'},'
                medrequ=medrequ+'"authoredOn": "'+str(fechaPresc)+'",'
                medrequ=medrequ+'"id": "'+str(nanonumber)+'",'
                medrequ=medrequ+'"meta": {'
                medrequ=medrequ+'"versionId": "1",'
                medrequ=medrequ+'"lastUpdated": "'+str(fechaPresc)+'"'
               # medrequ=medrequ+'"lastUpdated": "2022-03-21T19:27:24.776Z"'
                medrequ=medrequ+'}'
                medrequ=medrequ+'}'
                medrequ=json.loads(medrequ);
                print(medrequ)
                respresc=requests.post("https://apiqa-receta.minsal.cl/v2/RequestGroup",headers={"Authorization":"Bearer "+presctoken,"Content-Type": "application/json"},json=medrequ);
                print (str(respresc.status_code)+'::::'+respresc.text)
                if respresc.status_code==200 :
                    stmtup="UPDATE orderPrescriptions SET status='P' WHERE order_id='"+resul+"'"
                    openmrscursor.execute(stmtup);
                    openmrsdb.commit();
                    remitente = "contacto@isaprefundacion.cl"
                    destinatario = destinatario
                    mensaje = "¡<strong>Hola</strong>, <em>mundo</em>!"
                    email = EmailMessage()
                    email["From"] = remitente
                    email["To"] = destinatario
                    email["Subject"] = "Prescripcion enviada a ministerio"
                    email.set_content(mensaje, subtype="html")
                    smtp = smtplib.SMTP_SSL("smtp.ejemplo.com")
                    # O si se usa TLS:
                    # smtp = SMTP("smtp.ejemplo.com", port=587)
                    # smtp.starttls()
                    smtp.login(remitente, "Fund4c10n.123")
                    smtp.sendmail(remitente, destinatario, email.as_string())
                    smtp.quit()
                else :
                    logging.basicConfig(filename="apiprescription.txt", level=logging.DEBUG)
                    logging.error(medrequ)
            except:
                True
            time.sleep(5)
app.run();