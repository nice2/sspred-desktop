import time
import math
import requests
from guerrillamail import GuerrillaMailSession
import html
from bs4 import BeautifulSoup
#Contains functions related to output that are meant to be applied to multiple scripts

#Creates a random string to use for a prediction name. Can take a time and create a string from that
def randBase62(givenTime = None):
	if givenTime:
		integer = round(givenTime * 100000)
	else:
		integer = round(time.time() * 100000)
	chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
	result = ''
	while integer > 0:
		integer, remainder = divmod(integer, 62)
		result = chars[remainder]+result
	return result
	
#Takes current completed outputs and conducts a majority vote then returns it. If a majority vote results in an equal value, currently defaults to 'X'
def majorityVote(seq, ssObject):
	output = ''
	if len(ssObject) >= 2: #vote only if more than 2 ssObjects exist (at least 2 predictions)
		#create a counter for each character appearance
		seqLength = len(seq)
		cCount = [0] * seqLength
		hCount = [0] * seqLength
		eCount = [0] * seqLength
		
		for i in ssObject:
			if i.status == 1 or i.status == 3:
				for j in range(0, seqLength):
					if i.pred[j] == 'C':
						cCount[j] += 1
					elif i.pred[j] == 'E':
						eCount[j] += 1
					elif i.pred[j] == 'H':
						hCount[j] += 1

		for i in range(0, seqLength):
			if eCount[i] > hCount[i] and eCount[i] > cCount[i]:
				output += 'E'
			elif hCount[i] > cCount[i] and hCount[i] > eCount[i]:
				output += 'H'
			elif cCount[i] > hCount[i] and cCount[i] > eCount[i]:
				output += 'C'
			else:
				output += 'X' #use X if unsure - typically shows when not all predictions are completed
	else:
		return None
	return output

def pdbget(pdbid, chain):
	url = 'https://www.rcsb.org/pdb/explore/sequenceText.do?structureId=' + pdbid + '&chainId=' + chain

	r = requests.get(url)

	soup = BeautifulSoup(r.text, 'html.parser')

	cells = soup.findAll("td", {"class": "reportsequence"}) #get all rows with class name reportsequence

	if cells == []:
		#For invalid input
		return None

	sequence = ''
	color = []
	secondary = ''

	count = -4
	for cell in cells:
		if cell.has_attr('title'): # sequence rows have a title attribute
			letters = cell.findChildren("font") 
			#gets all elements with font attribute; these are all the letters in the primary sequence
			for letter in letters:
				#append letters and colors to list
				sequence += letter.text
				color.append(letter.attrs['color'])
		else:
			#every 6th cell after the 4th cell displays secondary structure
			if count %6 == 0:
				secondary+=cell.text
			count += 1


	secondary = secondary.replace('\n','') #remove all newlines
	secondarylist = list(secondary) #convert string to list
	del secondarylist[10::11] #remove every 11th element (spacing dividers)

	#convert list back to string
	secondary = '' 

	for i in secondarylist:
		secondary += i

	result = {
		'pdbid': pdbid, 
		'chain': chain,
		'primary': sequence,
		'color': color,
		'secondary': secondary
	}


	return result
	
#No auto canceling, infinite wait time

#Takes url to check, optional message for printing and optional sleep time in seconds. Defaults to 20 sec sleep time
#Returns the url when successful
def requestWait(requesturl, message = None, sleepTime = 20):
	while not requests.get(requesturl).ok:
		print(message)
		time.sleep(sleepTime)		
	return requests.get(requesturl)
	
#Takes a guerillamail session, search query, identifier line (Name: or Query:), and input name. Optional print message, and time to wait between checks
#Returns the bool email id and message when successful
def emailRequestWait(session, query, findLine, randName, printmsg = '', sleepTime = 60):
	message  = ''
	email_id = False
	
	while message == '': #loops until desired email is found or 15 min elapse
		print(printmsg)
		time.sleep(sleepTime)
		for e in session.get_email_list():			#For each email in inbox
			data = session.get_email(e.guid).body	#gets body of email
			if data is not None:					#Checks if email body is empty
				for dline in data.splitlines():		#Splits body into lines
					if findLine in dline:			#Checks if Query: line exists
						if dline[len(findLine):].strip() == randName:	#Checks if query is same as inputed seq name
							message = html.unescape(data)	#Sets message variable to email contents
							email_id = True			
	return email_id, message


'''
#Auto canceling versions
#Takes url to check, optional message for printing, and optional sleep time and cancel time in seconds. Defaults to 20 sec sleep time, 15 min wait to cancel
#Returns the url when successful
#Returns the url when successful
def requestWait(requesturl, message = None, sleepTime = 20 , cancelAfter = 900):
	stime  = time.time()
	
	while not requests.get(requesturl).ok and time.time() < stime + cancelAfter: #loops until requesturl is found or cancelAfter min elapse
		print(message)
		time.sleep(sleepTime)
	return requests.get(requesturl)
	
#Takes a guerillamail session, search query, identifier line (Name: or Query:), and input name. Optional print message, time to wait between checks, and how long to wait until cancelling (both in seconds)
#Returns the bool email id and message when successful
def emailRequestWait(session, query, findLine, randName, printmsg = '', sleepTime = 60, cancelAfter = 900):
	message  = ''
	stime = time.time()
	
	while message == '' and time.time() < stime + cancelAfter: #loops until desired email is found or cancelAfter min elapse
		print(printmsg)
		time.sleep(sleepTime)
		for e in session.get_email_list():			#For each email in inbox
			data = session.get_email(e.guid).body	#gets body of email
			if data is not None:					#Checks if email body is empty
				for dline in data.splitlines():		#Splits body into lines
					if findLine in dline:			#Checks if Query: line exists
						if dline[len(findLine):].strip() == randName:	#Checks if query is same as inputed seq name
							message = html.unescape(data)	#Sets message variable to email contents
							email_id = True
	return email_id, message
'''