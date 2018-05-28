#-*- coding: UTF-8 -*-   
#!/usr/bin/python
import smtplib
import os.path as op
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import datetime

def send_mail(send_from = 'flowers_mail@126.com', send_to = ['403270940@qq.com','2094562531@qq.com'], subject = 'flowers', 
            message = '', files=[],server="smtp.126.com", port=25, 
            username='flowers_mail@126.com', password='1234asdfASDF',use_tls=False):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (str): to name
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    """
    msg = MIMEMultipart()
    # msg['From'] = send_from
    # msg['To'] = COMMASPACE.join(send_to)
    # msg['Date'] = formatdate(localtime=True)
    # msg['Subject'] = subject

    msg['From'] = "{}".format(send_from)
    msg['To'] = ",".join(send_to)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(op.basename(path)))
        msg.attach(part)

    smtp = smtplib.SMTP_SSL(server,465)
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()
