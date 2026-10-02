# Copyright (C) 2018-2023 Mark McIntyre

from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
import smtplib
import os


def sendAnEmail(recipients, body, subject, sender='ukmeteors@gmail.com', files=None, passwd=None, msg_html=None):
    """
    Send an email via google, using the ukmeteors@gmail.com account.
    The app password for this account is stored in an SSM variable, if you want to use
    a different account you must pass the app password in to the function. 

    Arguments:  
        mailrecip:  [string] comma-separated string containing email addresses of recipients.  
        message:    [string] the message to send.  
        subject:    [string] Subject line.  

    Keyword Args:
        sender:     [string] email address of sender. Default 'ukmeteors@gmail.com' 
        passwd:     [string] 16-character app password created in google. Default read from SSM. 
        msg_html:   [string] HTML version of the message body, if any. 
        files:      [list]   list of files to attach - supports jpg, png, bmp. Want to support txt and pdf

        Returns:  
            Nothing, though a message is printed onscreen.  
    """

    if passwd is None:
        ssm = boto3.client('ssm', region_name='eu-west-2')
        res = ssm.get_parameter(Name='prod_gmailkey', WithDecryption=True)
        passwd = res['Parameter']['Value']

    msg = EmailMessage()
    msg['To'] = recipients
    msg['From'] = sender
    msg['Subject'] = subject
    msg.set_content(body)
    if msg_html:
        msg.add_alternative(msg_html, subtype="html")
    if files:
        for file in files:
            extn = os.path.splitext(file)[1]
            if extn in ['.jpg','.png','.bmp']:
                img_data = open(file, 'rb').read()
                msg.add_attachment(img_data, maintype='image', subtype=extn[1:])

    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
    smtp_server.login(sender, passwd)
    smtp_server.send_message(msg, sender, recipients)
    smtp_server.quit()
    smtp_server.close()
    return 


def test():
    subject = 'testing'
    body = 'Test for new from address for daily report'
    html_body = '<html><body><h2>test</h2>some text<br><li>foo</li></body></html>'
    recipients = 'markmcintyre99@googlemail.com'
    sendAnEmail(recipients, body, subject, msg_html=html_body)