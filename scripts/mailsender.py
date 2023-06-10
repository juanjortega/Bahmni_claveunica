import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# me == my email address
# you == recipient's email address
me = "contacto@centromedicofundacion.cl"
you = "r.cofret@gmail.com"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Emisión de prescripción en ministerio de salud"
msg['From'] = me
msg['To'] = you
# Create the body of the message (a plain-text and an HTML version).
html = """\
<html lang="en">
<head>
    <title>Receta Electronica</title>
</head>
<body style="font: 13px arial, helvetica, tahoma;">
<div class="email-container" style="width: 650px; border: 1px solid #eee;">
    <div id="header" style="background-color: #429a82; height: 45px; padding: 10px 15px;">
        <strong id="logo" style="color: white; font-size: 20px; margin-top: 10px; display: inline-block">
            Isapre Fundación
        </strong>
    </div>

    <div id="content" style="padding: 10px 15px;">
        <h2>Receta electronica</h2>
        <p>Se ha enviado la siguiente prescripción al ministerio de salud</p>
        <table id="customer-details">
            <tr>
                <td class="label" style="padding: 3px;font-weight: bold;"><?= lang('name') ?></td>
                <td style="padding: 3px;"><strong>Medicamento :</strong>Ibuprofeno</td>
            </tr>
            <tr>
                <td class="label" style="padding: 3px;font-weight: bold;"><?= lang('email') ?></td>
                <td style="padding: 3px;"><strong>Unidad :</strong>100 mg</td>
            </tr>
            <tr>
                <td class="label" style="padding: 3px;font-weight: bold;"></td>
                <td style="padding: 3px;"><strong>Paciente :</strong>Juan Perez Cotapo</td>
            </tr>

        </table>
<!--
        <h2></h2>
        <a href="<?= $appointment_link ?>" style="width: 600px;"><?= $appointment_link ?></a>
-->

        <p>Ante cualquier duda o dificultad, escríbanos a telemedicina@centromedicofundacion.cl o llámenos al 223479204.</p>
    </div>

    <div id="footer" style="padding: 10px; text-align: center; margin-top: 10px;
                border-top: 1px solid #EEE; background: #FAFAFA;">
        Powered by
        <a href="https://easyappointments.org" style="text-decoration: none;">Easy!Appointments</a>
        |
        
    </div>
</div>
</body>
</html>




"""

# Record the MIME types of both parts - text/plain and text/html.
#part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
#msg.attach(part1)
msg.attach(part2)
# Send the message via local SMTP server.
mail = smtplib.SMTP("mail.centromedicofundacion.cl")

mail.ehlo()



mail.sendmail(me, you, msg.as_string())
mail.quit()