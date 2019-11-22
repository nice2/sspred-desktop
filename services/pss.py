import requests
from bs4 import BeautifulSoup
import time

from services import ss, batchtools

def get(seq, email_address):

	SS = ss.SS("PSS")
	SS.status = 0
	
	if time.time() < 1571702400.00:
		SS.pred = "PSS down until Oct 22"
		SS.conf = "PSS down until Oct 22"
		SS.status = 2
		return SS

	if (len(seq) > 4000):
		SS.pred += "Sequence longer than 4000"
		SS.conf += "Sequence longer than 4000"
		SS.status = 2 #error status
		print("PSSPred failed: Sequence longer than 4000")
		return SS #return SS so it will be readable as an ssObject
		
	payload = {'REPLY-E-MAIL': email_address, 
		'TARGET-NAME': 'testprot', 
		'SEQUENCE': seq}
	
	#Around 15 min for 4000
	r= requests.post('https://zhanglab.ccmb.med.umich.edu/cgi-bin/PSSpred.pl', data=payload)

	soup = BeautifulSoup(r.text, 'html.parser')
	
	#Exit if no links available in the response
	if soup.a is None: 
		SS.pred = "Failed to submit, server possibly under load"
		SS.conf = "Failed to submit, server possibly under load"
		SS.status = 2
		return SS

	ssurl = soup.a.get('href')

	ssurl = ssurl + '/seq.SS'
	
	'''
	while not requests.get(ssurl).ok:
		print('PSSpred Not Ready')
		time.sleep(20)

	raw = requests.get(ssurl).text.splitlines()
	'''
	
	requesturl = batchtools.requestWait(ssurl, "PSSpred Not Ready")

	if requesturl:
		raw = requesturl.text.splitlines()
		for i in range(len(raw)):
			if raw[i].startswith("conf"):
				SS.conf += raw[i][6:].strip()
			if raw[i].startswith("SS"):
				SS.pred += raw[i][6:].strip()

		SS.status = 1
		print("PSSPred Complete")
	else:
		SS.pred += "PSSPred failed to respond in time"
		SS.conf += "PSSPred failed to respond in time"
		SS.status = 2 #error status
		print("PSSPred failed: No response")
	return SS