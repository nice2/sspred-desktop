import requests
import time

from services import ss


def get(seq, email_address):

	SS = ss.SS("JPred")
	
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
	
	if page[0] != '<':
		raw = page.splitlines()

		SS.pred = raw[1].replace('jnetpred:','')
		SS.pred = SS.pred.replace('-','C')			#Replaces dashes with C
		SS.pred = SS.pred.replace(',','')

		SS.conf = raw[2].replace('JNETCONF:','')
		SS.conf = SS.conf.replace(',','')

		SS.status = 1
		print("JPred Complete")
	else:
		SS.pred += "JPred failed to respond in time"
		SS.conf += "JPred failed to respond in time"
		SS.status = 2 #error status
		print("JPred failed: No response")
	
	print("JPRED::")
	print(SS.pred)
	print(SS.conf)
	return SS