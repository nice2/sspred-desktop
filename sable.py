import os
import requests
import time
import io
import re

import emailtools
import ss

SS = ss.SS("Sable")
SS.status = 0

def get(seq, email_address, email_service):

	randName = emailtools.randBase62()

	payload = {'txtSeq': seq, 
	'seqName': randName,
	'email': email_address, 
	'fileName':'', 
	'SS':'SS', 
	'version':'sable2', 
	'SAaction': 'wApproximator',
	'SAvalue':'REAL'}
	
	r = requests.post('http://sable.cchmc.org/cgi-bin/sable_server_July2003.cgi', data = payload)
	
	#sable uses multiple emails to send results
	query = 'from:(sable) subject:(sable result) query: ' + randName
	
	email_id = emailtools.searchEmailId(email_service, query)
	
	while(email_id == -1):
		print('Sable Not Ready')	
		time.sleep(60)
		email_id = emailtools.searchEmailId(email_service, query)
	
	message = emailtools.decodeEmail(email_service, email_id)
	message_parts = message.splitlines()

	#getting the prediction sequence and confidence
	index = 0
	while message_parts[index] != 'END_SECTION':
		if message_parts[index].startswith('>'):
			SS.pred += message_parts[index + 2].strip()
			SS.conf += message_parts[index + 3].strip()
			index + 4 #add 4 then 1 later to get to next set of prediction
		index += 1

	#getting the probabilities for helix, beta strand, coil
	index += 1 #go past the prediction's 'END_SECTION'
	helixProb = ''
	betaProb = ''
	coilProb = ''
	while message_parts[index] != 'END_SECTION':
		if message_parts[index].startswith('>'):
			helixProb += message_parts[index + 2][3:].strip() + ' '
			betaProb += message_parts[index + 3][3:].strip() + ' '
			coilProb += message_parts[index + 4][3:].strip() + ' '
		index += 1
		
	SS.hconf = helixProb.split()
	SS.econf = betaProb.split()
	SS.cconf = coilProb.split()
	
	SS.status = 1
	print("Sable Complete")
	return SS