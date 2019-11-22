import os
import requests
import time
import io
import re
from bs4 import BeautifulSoup

from services import ss, emailtools, batchtools

def get(seq, email_address):
	
	SS = ss.SS("SSPro")
	SS.status = 0
	
	if (len(seq) > 400):
		SS.pred += "Sequence longer than 400"
		SS.conf += "Sequence longer than 400"
		SS.status = 2 #error status
		print("SSPro failed: Sequence longer than 400")
		return SS #return SS so it will be readable as an ssObject
	
	randName = batchtools.randBase62()
	
	payload = {'amino_acids': seq,
	'query_name': randName, 
	'email': email_address,
	'ss':'on'}
	
	r = requests.post('http://scratch.proteomics.ics.uci.edu/cgi-bin/new_server/sql_predict.cgi', data = payload)

	soup = BeautifulSoup(r.text, 'html.parser')
	msg = soup.find('p')
	if msg == None:
		SS.pred += "Failed to Submit"
		SS.conf += "Failed to Submit"
		SS.status = 2 #error status
		print("SSPro Failed to Submit")
		return SS

	if msg.text.split()[0] == 'ERROR:':
		SS.pred += "Queue Full"
		SS.conf += "Queue Full"
		SS.status = 2 #error status
		print("SSPro Queue Full")
		return SS
	
	query = 'from:(baldig@ics.uci.edu) subject:(Protein Structure Predictions for ' + randName + ')'
	email_service = emailtools.login()
	
	'''
	email_id = emailtools.searchEmailId(email_service, query)
	while(email_id == -1):
		print('SSPro Not Ready')	
		time.sleep(60)
		email_id = emailtools.searchEmailId(email_service, query)
	'''
	
	#Length 400 sequences take 10-15 min in a batch
	email_id = batchtools.emailRequestWait(email_service, query, "SSPro Not Ready")
	
	if email_id:
		message = emailtools.decodeEmail(email_service, email_id)
		message_parts = message.splitlines()
		
		index = 0 #current line
		finished_scrape = False
		
		while index < len(message_parts) and not finished_scrape:
			index += 1
			if message_parts[index] == "Predicted Secondary Structure (3 Class):":
				while message_parts[index]: #while not blank line
					index += 1
					SS.pred += message_parts[index]
				finished_scrape = True

		SS.conf = "SSPro Does Not Provide Any Conf" 
		SS.status = 3
		print("SSpro Complete")
	else:
		SS.pred += "SSPro failed to respond in time"
		SS.conf += "SSPro failed to respond in time"
		SS.status = 2 #error status
		print("SSPro failed: No response")
	return SS