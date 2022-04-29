import os
import sys
import base64
#from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES =['https://mail.google.com/']


def getGmailCreds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    tokfile = os.path.expanduser('~/.ssh/gmailtoken.json')
    crdfile = os.path.expanduser('~/.ssh/gmailcreds.json')
    if os.path.exists(tokfile):
        creds = Credentials.from_authorized_user_file(tokfile, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(crdfile, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokfile, 'w') as token:
            token.write(creds.to_json())
    return creds


def create_message(sender, to, subject, message_text):
    msg = MIMEText(message_text)
    msg['to'] = to
    msg['from'] = sender
    msg['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode('utf-8')).decode('utf-8')}



def sendAnEmail(mailrecip, message, msgtype, files=None):
    hname = 'ukmonhelper' # os.uname()[1]

    # email a summary to the mailrecip
    creds = getGmailCreds()
    service = build('gmail', 'v1', credentials=creds)

    subj ='{:s}: {:s}'.format(hname, msgtype)
    message = '{:s}: {:s}'.format(msgtype, message)

    mailmsg = create_message('mjmm456@gmail.com', mailrecip, subj, message)

    try:
        retval = (service.users().messages().send(userId='me', body=mailmsg).execute())
        print('Message Id: %s' % retval['id'])
    except:
        print('An error occurred sending the message')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: sendAnEmail.py recipient "message in quotes" Alert|Warning|Error ')
    else:
        sendAnEmail(sys.argv[1], sys.argv[2], sys.argv[3])
