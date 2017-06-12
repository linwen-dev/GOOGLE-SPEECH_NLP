from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import base64
import os

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'gmail_api_data.json'
APPLICATION_NAME = 'Drive API Python Quickstart'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class GmailApi:
    def __init__(self):
        self.credentials = self.get_credentials()
        self.service = discovery.build(serviceName='gmail', version='v1', credentials=self.credentials)

    def get_credentials(self):
        """Gets valid user credentials from storage.
    
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
    
        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'gmail-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def get_all_messages(self):
        response = self.service.users().messages().list(userId='me', q='').execute()
        return response

    def get_unread_messages(self, page_token=False, q=''):
        if page_token:
            response = self.service.users().messages().list(userId='me', q='is:unread '+q, pageToken=page_token).execute()
        else:
            response = self.service.users().messages().list(userId='me', q='is:unread '+q).execute()
        return response

    def get_read_messages(self, page_token=False):
        if page_token:
            response = self.service.users().messages().list(userId='me', q='is:read', pageToken=page_token).execute()
        else:
            response = self.service.users().messages().list(userId='me', q='is:read').execute()
        return response

    def get_message_by_id(self, message_id):
        response = self.service.users().messages().get(userId='me', id=message_id).execute()
        return response

    def get_message_body(self, message):
        return base64.urlsafe_b64decode(message['payload']['parts'][0]['body']['data']).decode()

    def modify_message_labels(self, message_id, message_labels):
        message = self.service.users().messages().modify(userId='me', id=message_id, body=message_labels).execute()
        return message

    def mark_message_as_read(self, message_id):
        return self.modify_message_labels(message_id, {'removeLabelIds': ['UNREAD']})

    def mark_all_messages_as_read(self):
        response = self.get_unread_messages()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.get_unread_messages(page_token=page_token)
            messages.extend(response['messages'])
        for message in messages:
            self.mark_message_as_read(message_id=message['id'])

    def mark_message_as_unread(self, message_id):
        return self.modify_message_labels(message_id, {'addLabelIds': ['UNREAD']})

    def mark_all_messages_as_unread(self):
        response = self.get_read_messages()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.get_read_messages(page_token=page_token)
            messages.extend(response['messages'])
        for message in messages:
            self.mark_message_as_unread(message_id=message['id'])

    def send_message(self, message):
        message = (self.service.users().messages().send(userId='me', body=message).execute())
        return message

    def create_message(self, sender, to, subject, message_text):
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        message.attach(MIMEText(message_text, 'plain'))
        raw_message = base64.urlsafe_b64encode(message.as_string())
        return {'raw': raw_message}

# gmail = GmailApi()
# gmail.mark_all_messages_as_read()
# message = gmail.create_message('voice2mail@tenence.com', 'voice2mail@tenence.com', 'Some random subject', "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")
# print(gmail.send_message(message))
# print(gmail.retrive_unread_messages())
# print(base64.urlsafe_b64decode(gmail.retrieve_message_by_id('15c18f6286656e79')['payload']['parts'][0]['body']['data']).decode())
# response = gmail.retrieve_message_by_id('15c18c422902ed1a')
# print(response)
#
# response = gmail.mark_message_as_unread('15c18c422902ed1a')
# for header in response['payload']['headers']:
#     if header['name'] == 'Subject':
#         print(header['value'])
#         break

