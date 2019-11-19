import time
import math
import requests
from services import emailtools
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

#Takes url to check, optional message for printing, optional sleep time in seconds,and optional time in seconds to stop waiting. Defaults to 20 sec sleep time, 20 min wait time
#Returns the url if successful within the allowed wait time, and None otherwise
def requestWait(requesturl, message = None, sleepTime = 20, cancelAt = 1200):
	totalSleepTime = 0
	while not requests.get(requesturl).ok:
		if totalSleepTime >= cancelAt:
			return None
		print(message)
		time.sleep(sleepTime)
		totalSleepTime += sleepTime
		
	return requests.get(requesturl)
	
#Same as request wait but with emails. Default sleeps for 1 min at a time
def emailRequestWait(email_service, query, message = None, sleepTime = 60, cancelAt = 1200):
	totalSleepTime = 0
	email_id = emailtools.searchEmailId(email_service, query)
	while(email_id == -1):
		if totalSleepTime >= cancelAt:
			return None
		print(message)
		time.sleep(sleepTime)
		totalSleepTime += sleepTime
		email_id = emailtools.searchEmailId(email_service, query)
	return email_id
	