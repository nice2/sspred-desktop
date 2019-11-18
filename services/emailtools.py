import pickle
import email
import os.path
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

#Logs in using token.pickle
def login():
	creds = None
	if os.path.exists('services/token.pickle'):
		with open('services/token.pickle', 'rb') as token:
			#print("opened pickle")
			creds = pickle.load(token)
		
	#Refresh if needed
	if creds and creds.expired and creds.refresh_token:
		creds.refresh(Request())

	service = build('gmail', 'v1', credentials=creds)
	
	return service

#Gets email address
def getEmailAddress(service):
	address = service.users().getProfile(userId='me').execute()
	return address['emailAddress']

#Returns the first email id that matches the query, -1 if not found
#Query guide: https://support.google.com/mail/answer/7190
#OR use the advanced search on the browser version of gmail and use that as the query
def searchEmailId(service, query):
	messageList = service.users().messages().list(userId='me',q=query).execute()
	
	if 'messages' in messageList:
		message = []
		message.extend(messageList['messages'])
		id = message[0]['id']
		message = service.users().messages().get(userId='me', id=id, format='raw').execute()
		return id
	return -1 #email not found

#Takes an email id and converts the 'raw' format of the email body to string
def decodeEmail(service, emailId):
	message = service.users().messages().get(userId='me', id=emailId, format='raw').execute()
	msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
	mime_msg = email.message_from_bytes(msg_str).as_string()
	return mime_msg
	
#Create token.pickle. Needed to change emails or update scopes
def createPickle():
	flow = InstalledAppFlow.from_client_secrets_file('services/credentials.json', SCOPES)
	creds = flow.run_local_server(port=0)
	# Save the credentials for the next run
	with open('services/token.pickle', 'wb') as token:
		pickle.dump(creds, token)
