import requests
from bs4 import BeautifulSoup
import time

import ss

SS = ss.SS("PSS")
SS.status = 0

def get(seq, email_address, email_service):
	
	if (len(seq) >= 4000):
		SS.pred += "Sequence longer than 4000"
		SS.conf += "Sequence longer than 4000"
		SS.status = 2 #error status
		print("PSSPred failed: Sequence longer than 4000")
		return SS #return SS so it will be readable as an ssObject
		
	payload = {'REPLY-E-MAIL': email_address, 
		'TARGET-NAME': 'testprot', 
		'SEQUENCE': seq}

	r= requests.post('https://zhanglab.ccmb.med.umich.edu/cgi-bin/PSSpred.pl', data=payload)

	soup = BeautifulSoup(r.text, 'html.parser')

	ssurl = soup.a.get('href')

	ssurl = ssurl + '/seq.SS'

	while not requests.get(ssurl).ok:
		print('PSSpred Not Ready')
		time.sleep(20)

	raw = requests.get(ssurl).text.splitlines()


	for i in range(len(raw)):
		if raw[i].startswith("conf"):
			SS.conf += raw[i][6:].strip()
		if raw[i].startswith("SS"):
			SS.pred += raw[i][6:].strip()

	SS.status = 1
	print("PSSPred Complete")
	return SS