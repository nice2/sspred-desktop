import os
import requests
import time
import io
import re

import emailtools
import ss

SS = ss.SS("SSPro")
SS.status = 0


def get(seq, email_address, email_service): #may need to check if all slots in queue are taken

	if (len(seq) > 400):
		SS.pred += "Sequence longer than 400"
		SS.conf += "Sequence longer than 400"
		SS.status = 2 #error status
		print("SSPro failed: Sequence longer than 400")
		return SS #return SS so it will be readable as an ssObject
	
	randName = emailtools.randBase62()
	
	payload = {'amino_acids': seq,
	'query_name': randName, 
	'email': email_address,
	'ss':'on'}
	
	r = requests.post('http://scratch.proteomics.ics.uci.edu/cgi-bin/new_server/sql_predict.cgi', data = payload)
	
	query = 'from:(baldig@ics.uci.edu) subject:(Protein Structure Predictions for ' + randName + ')'
	email_id = emailtools.searchEmailId(email_service, query)
	
	while(email_id == -1):
		print('SSPro Not Ready')	
		time.sleep(60)
		email_id = emailtools.searchEmailId(email_service, query)
	
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
	SS.status = 1
	print("SSpro Complete")
	return SS
