import requests
import time
from guerrillamail import GuerrillaMailSession

from services import ss, batchtools

def get(seq):

	SS = ss.SS("Yaspin")
	SS.status = 0

	if (len(seq) > 4000):
		SS.pred += "Sequence longer than 4000"
		SS.conf += "Sequence longer than 4000"
		SS.status = 2 #error status
		print("YASPIN failed: Sequence longer than 4000")
		return SS #return SS so it will be readable as an ssObject
		
	session = GuerrillaMailSession()	#Creates GuerrillaMail session
	email_address = session.get_session_state()['email_address'] #retrieves temp email address
	
	payload = {'seq': seq,
	'mbjob[description]': 'testprot',
	'nnmethod': 'dssp', 
	'smethod': 'nr', 
	'yaspin_align': 'YASPIN prediction', 
	'email': email_address}
	
	fasta = {'seq_file': ''}
	r= requests.post('http://www.ibi.vu.nl/programs/yaspinwww/', data = payload, files = fasta)
	
	if (r.status_code == 500):
		SS.pred += "Server Down"
		SS.conf += "Server Down"
		SS.status = 2
		print("Yaspin Failed: Server Down")
		return SS
	
	result_url = r.url + 'results.out'
	
	requesturl = batchtools.requestWait(result_url, 'Yaspin Not Ready')
	
	if requesturl:
		raw = requesturl.text.splitlines()
		
		for i in range(len(raw)):		
			if raw[i].startswith(" Pred:"):
				SS.pred += raw[i][6:].strip()
			if raw[i].startswith(" Conf:"):
				SS.conf += raw[i][6:].strip()
		
		SS.pred = SS.pred.replace('-','C')

		SS.status = 1
		print("Yaspin Complete")
	else:
		SS.pred += "Yaspin failed to respond in time"
		SS.conf += "Yaspin failed to respond in time"
		SS.status = 2 #error status
		print("YASPIN failed: No response")
	return SS