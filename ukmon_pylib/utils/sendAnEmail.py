import os
import sys
import configparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendAnEmail(mailrecip, message, msgtype, files=None):
    hname = 'ukmonhelper' # os.uname()[1]

    # email a summary to the mailrecip
    smtphost = os.getenv('MAILHOST') # localcfg['gmail']['mailhost'].rstrip()
    smtpport = os.getenv('MAILPORT') # int(localcfg['gmail']['mailport'].rstrip())
    smtpuser = os.getenv('MAILUSER') # localcfg['gmail']['mailuser'].rstrip()
    smtppwd = os.getenv('MAILPWD')   # localcfg['gmail']['mailpwd'].rstrip()
    with open(os.path.expanduser(smtppwd), 'r') as fi:
        line = fi.readline()
        spls=line.split('=')
        smtppass=spls[1].rstrip()

    s = smtplib.SMTP(smtphost, smtpport)
    s.starttls()
    s.login(smtpuser, smtppass)
    msg = MIMEMultipart()

    msg['From']='pi@{:s}'.format(hname)
    msg['To']=mailrecip

    msg['Subject']='{:s}: {:s}'.format(hname, msgtype)
    message = '{:s}: {:s}'.format(msgtype, message)
    msg.attach(MIMEText(message, 'plain'))
    try:
        s.sendmail(msg['From'], mailrecip, msg.as_string())
    except:
        print('unable to send mail')

    s.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: sendAnEmail.py recipient, "message in quotes" Alert|Warning|Error ')
    else:
        sendAnEmail(sys.argv[1], sys.argv[2], sys.argv[3])
