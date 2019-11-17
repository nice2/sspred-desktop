import requests
import time

import ss

SS = ss.SS("JPred")

def get(seq, email_address, email_service):

	if (len(seq) < 20 or len(seq) > 800):
		SS.pred += "Sequence is shorter than 20 or longer than 800"
		SS.conf += "Sequence is shorter than 20 or longer than 800"
		SS.status = 2 #error status
		print("JPred failed: Sequence is shorter than 20 or longer than 800")
		return SS #return SS so it will be readable as an ssObject
	
	payload = {'email': email_address, 
		'queryName': 'testprot', 
		'input': 'seq', 
		'pdb': '1', 
		'.submit': 'continue', 
		'seq': seq}

	r= requests.post('http://www.compbio.dundee.ac.uk/jpred4/cgi-bin/jpred_form', data=payload)

	response = r.headers['Refresh'].split('?')
	jobid = response[1]

	joburl = 'http://www.compbio.dundee.ac.uk/jpred4/results/' + jobid + '/' + jobid + '.jnet'

	page = requests.get(joburl).text

	while page[0] == '<':
		print("JpredSS Not Ready")
		time.sleep(20)
		page = requests.get(joburl).text



	raw = page.splitlines()

	SS.pred = raw[1].replace('jnetpred:','')
	SS.pred = SS.pred.replace('-','C')			#Replaces dashes with C
	SS.pred = SS.pred.replace(',','')

	SS.conf = raw[2].replace('JNETCONF:','')
	SS.conf = SS.conf.replace(',','')

	SS.status = 1
	print("JPred Complete")
	return SS