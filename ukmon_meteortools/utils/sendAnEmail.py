# Copyright (C) 2018-2023 Mark McIntyre
import os
import sys
import platform
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES =['https://mail.google.com/']


def _getGmailCreds():
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
            if not os.path.isfile(crdfile):
                print('to use this function you must have stored your Google OAUTH2 secret json file in ~/.ssh/gmailcreds.json.')
                print('To set up OAUTH2 go to your google cloud console, select APIs then Credentials, and add an OAUTH2 desktop client ID.')
                return None
            flow = InstalledAppFlow.from_client_secrets_file(crdfile, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokfile, 'w') as token:
            token.write(creds.to_json())
    return creds


def _create_message(sender, to, subject, message_text):
    msg = MIMEText(message_text)
    msg['to'] = to
    msg['from'] = sender
    msg['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode('utf-8')).decode('utf-8')}



def sendAnEmail(mailrecip, message, msgtype, mailfrom, files=None):
    """ sends an email using gmail. 
    
        Arguments:  
            mailrecip:  [string] email address of recipient.  
            message:    [string] the message to send.  
            msgtype:    [string] Prefix for the subject line, eg Test, Warning.  
            mailfrom:   [string] email address of sender.   
            files:      [list]   list of files to attach, not currently implemented.  

        Returns:  
            Nothing, though a message is printed onscreen.  

        Notes:  
            You must have gmail OAUTH2 set up. The gmail credentials must be stored as follows:  
                token: $HOME/.ssh/gmailtoken.json  
                creds: $HOME/.ssh/gmailcreds.json  

            On Windows, $HOME corresponds to c:/users/yourid. If there is no .ssh folder, create it.   
        """
    
    if msgtype is None:
        msgtype = platform.uname()[1]

    # email a summary to the mailrecip
    creds = _getGmailCreds()
    if not creds:
        return 
    service = build('gmail', 'v1', credentials=creds)

    subj ='{:s}: {:s}'.format(msgtype, message[:30])
    message = '{:s}: {:s}'.format(msgtype, message)

    mailmsg = _create_message(mailfrom, mailrecip, subj, message)

    try:
        retval = (service.users().messages().send(userId='me', body=mailmsg).execute())
        print('Message Id: %s' % retval['id'])
    except:
        print('An error occurred sending the message')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('usage: sendAnEmail.py recipient "message in quotes" Alert|Warning|Error sender ')
    else:
        sendAnEmail(sys.argv[1], sys.argv[2], sys.argv[3],sys.argv[4])
