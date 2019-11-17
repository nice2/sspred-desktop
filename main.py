from tkinter import * 
from tkinter import ttk
import time
import psi , pss, jpred, raptorx, yaspin, sable, sspro, ss
import threading, queue
import emailtools
import fileoutput
from multiprocessing.pool import ThreadPool		

q = queue.Queue()
service = [None] * 7
service[0] = psi
service[1] = pss
service[2] = jpred
service[3] = raptorx
service[4] = yaspin
service[5] = sable
service[6] = sspro

seq = 'MSAEREIPAEDSIKVVCRFRPLNDSEEKAGSKFVVKFPNNVEENCISIAGKVYLFDKVFKPNASQEKVYNMSAEREIPAEDSIKVVCRFRPLNDSEEKAGSKFVVKFPNNVEENCISIAGKVYLFDKVFKPNASQEKVYN'

#List of 18 Lines to display live output
ssList = [''] * 18

#Note of indices for output textbox
counterIndex = 0
seqIndex = 1
blankIndex = 9 # 10

#First value is Index for Prediction Line
#Second value is Index for Confidence Line
ssDict = {
	"PSI" : [2, 3],
	"PSS" : [4, 5],
	"JPred" : [6, 7],
	"RaptorX" : [8, 9],
	"YASPIN" : [10, 11],
	"Sable" : [12, 13],
	"SSPro" : [14, 15],
	}
'''
ssDict = {
	"PSI" : [2, 11],
	"PSS" : [3, 12],
	"JPred" : [4, 13],
	"RaptorX" : [5, 14],
	"YASPIN" : [6, 15],
	"Sable" : [7, 16],
	"SSPro" : [8, 17],
	}
'''
#List of ssObjects to be returned from each thread
ssObject = []


email_service = '' #for logging into email and accessing mail
email_address = ''

#Prints out character position every 10 characters until end of initial sequence; First line of output textbox
def drawCounter(mySeq):
	j=0
	p = 1

	ssList[0] = "\n"

	while j < len(mySeq):
		if j%10 != 0:
			ssList[0]+= ' '
			j = j+1
		else:
			for k in range(len(str(p))):
				ssList[0]+= str(str(p)[k])
				j=j+1
			p = p+10
	
#Fills output textbox line by line from ss list
def fillString():

	mystring = ssList[0]

	for i in range(1,len(ssList)):
		mystring += "\n" + ssList[i]

	updateText(outputText, mystring)
	colorCode()

	
#Takes current completed outputs and conducts a majority vote, then returns it. If a majority vote results in an equal value, currently defaults to 'C'
def majorityVote():
	output = ''
	if len(ssObject) >= 2: #vote only if more than 2 ssObjects exist (at least 2 predictions)
		seqLength = len(ssList[1]) - 1 #-1 to get rid of \n
		
		#create a counter for each character appearance
		cCount = [0] * seqLength
		hCount = [0] * seqLength
		eCount = [0] * seqLength
		
		for i in ssObject:
			if i.status == 1: #also check if the ssObject actually completed
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
	return output
	
#Disables any buttons/fields to prevent any more input when running
def disableInput():
	startButton['state'] = 'disabled'
	clearButton['state'] = 'disabled'
	seqText['state'] = 'disabled'

#Updates a given text widget. Enables then disables them if they were disabled
def updateText(textbox, text):
	if textbox['state'] == 'disabled':	
		textbox.configure(state='normal')
		textbox.delete(1.0, END)
		textbox.insert(1.0, text)
		textbox.configure(state='disabled')
	else:
		textbox.delete(1.0, END)
		textbox.insert(1.0, text)

#Color codes outputs with successful statuses. Helix = blue, Coil = red, Strand = yellow
def colorCode():
	for i in ssObject:
		if i.status == 1:
			index = 0
			textRow = ssList[ssDict[i.name][0]] #the line of output text to be colored
			baseRow = str(ssDict[i.name][0] + 3) #the row index to add onto, converted to string. add 3 to get the proper row (skips the empty first row, count row, sequence, and gap)
			while index < len(textRow):	
				#indices for tkinter texts require decimal strings such as 1.10,3.11,7.30 (1.10 and 7.30 are not the same as 1.1 and 7.3)
				start = baseRow + "." + str(index) 
				end = baseRow + "." + str(index + 1) #ends 1 space after start to cover 1 letter
				setColor(textRow[index], start, end)
				index += 1
				
	#color code majority vote			
	for i in range(0, len(ssList[-1])):
		setColor(ssList[-1][i], str(len(ssList) + 2) + "." + str(i), str(len(ssList) + 2) + "." + str(i + 1))

#Sets color to outputText with a given char, start index, and end index
def setColor(char, start, end):
	if char == 'H':
		outputText.tag_add("Helix", start, end)
	elif char == 'E':
		outputText.tag_add("Strand", start, end)
	elif char == 'C':
		outputText.tag_add("Coil", start, end)
		
#Saves the output to a txt and HTML file. Gives start time and list of outputs for processing.
#"pred month.day.year hr.min.sec" for file name
def savePrediction():
	fileoutput.createFolder(startTime)
	fileoutput.createTxt(startTime, ssList, ssObject)
	fileoutput.createHTML(startTime, ssList, ssObject)
	
#Takes an ssObject and time it was completed to update logText
def updateLog(ssObject, time):
	global log
	log += ssObject.name
	if(ssObject.status == 2):
		log += " ended with an error in "
	else:
		log += " finished in "
	log += time + "\n"
	
	updateText(logText, log)
	
#Loops every second, displaying time elapsed, checking if threads for each service has completed and updating ss list 	
def refresh():

	currentTime = time.strftime("%H:%M:%S", time.gmtime(time.time()-startTime))
	timeElapsed = "Time Elapsed: " + currentTime
	timeElapsedLabel.config(text = timeElapsed)
	
	#Gets ssObject returned from Thread from Queue
	#Uses SS.name value and ssDict to find position in textbox to display value
	if not q.empty():
		ssObject.append(q.get())
		ssList[ssDict[ssObject[-1].name][0]] = ssObject[-1].pred
		ssList[ssDict[ssObject[-1].name][1]] = ssObject[-1].conf
		ssList[-1] = majorityVote()
		fillString()
		updateLog(ssObject[-1], currentTime)
		
		
	if len(ssObject) < 7:
		root.after(1000, lambda: refresh())

#Used for second thread to prevent gui from hanging
def putinq(data, myq):
	myq.put(data.get())

#Disables sequence entry, disables button, creates threads for each service	
def run():
	global startTime
	startTime = time.time()	
	
	disableInput();
	startButton['text'] = 'Running...'	
	
	seq = ''.join(seqText.get(1.0,END).split())
	seqLengthLabel.config(text = "Sequence Length: " + str(len(seq)))
	ssList[1] = seq + "\n"
	drawCounter(seq)
	fillString()
	
	#Begin logging into the log box
	global log
	log = 'Started prediction on ' + time.asctime(time.localtime(startTime)) + '\n'
	updateText(logText, log)
	
	#creates 2 threads for each service
	#One to run the service and one to await output to place in Queue
	#Might be possible to reduce to one thread in each
	pool = ThreadPool(processes=len(service)*2)
	for i in range(len(service)):
		result = pool.apply_async(service[i].get, (seq, email_address, email_service))
		pool.apply_async(putinq, (result,q))
	
	refresh()
	
startTime = time.time()
log = '' #records current run of outputs

root = Tk()
root.title("Protein Sequence Secondary Structure Prediction Scraper")
root.geometry("800x600")

# Top Frame will contain inital sequence entry, control buttons, and current run status
topFrame = Frame(root)
topFrame.pack(side='top')

# Bottom Frame will contain Outputs
bottomFrame = Frame(root)
bottomFrame.pack(side='top', fill ='both', expand = True)

#Label reading "Sequence"
seqLabel = Label(topFrame, text="Sequence: ")
seqLabel.grid(row=0, column=0, sticky = W)

#Frame containing input textbox and vertical scroller
seqTextFrame = Frame(topFrame,borderwidth=1, relief="sunken")
seqText = Text(seqTextFrame, wrap = CHAR, height = 10, width = 40, borderwidth=0)
seqText.insert(1.0,"MSAEREIPAEDSIKVVCRFRPLNDSEEKAGSKFVVKFPNNVEENCISIAGKVYLFDKVFKPNASQEKVYNMSAEREIPAEDSIKVVCRFRPLNDSEEKAGSKFVVKFPNNVEENCISIAGKVYLFDKVFKPNASQEKVYN") #Sample Input
vscroll = Scrollbar(seqTextFrame, orient=VERTICAL, command=seqText.yview)
seqText['yscroll'] = vscroll.set
vscroll.pack(side="right", fill="y")
seqText.pack(side="left", fill="both", expand=True)
seqTextFrame.grid(row=1, column = 0, padx = 5, sticky = W)

#Frame containing control buttons
controlFrame = Frame(topFrame)
controlFrame.grid(row = 1, column = 1, padx = 20)
startButton = Button(controlFrame, text="Start", command = run) #Button to start run function
startButton.grid(row = 0, column = 0, pady = 10)
clearButton = Button(controlFrame, text="Clear Sequence", command = lambda: updateText(seqText, '')) #Clears seqText
clearButton.grid(row = 1, column = 0, pady = 10)
saveButton = Button(controlFrame, text="Save Predictions", command = savePrediction) #Saves output to txt file
#saveButton['state'] = 'disabled'
saveButton.grid(row = 3, column = 0)

#Frame containing status and log tabs
statusFrame = ttk.Notebook(topFrame)
statusTab = ttk.Frame(statusFrame)
logTab = ttk.Frame(statusFrame)
statusFrame.add(statusTab, text='Status')
statusFrame.add(logTab, text='Log')
statusFrame.grid(row = 1, column = 2)
#Status tab
seqLengthLabel = Label(statusTab, text="Sequence Length: ")
seqLengthLabel.grid(row = 0, column = 0, sticky= W)
timeElapsedLabel = Label(statusTab, text="Time Elapsed: 00:00:00")
timeElapsedLabel.grid(row = 2, column = 0, sticky= W)
#Log tab
logText = Text(logTab, wrap = CHAR, height = 8, width = 30, borderwidth=0)
logText['state'] = 'disabled'
vscroll2 = Scrollbar(logTab, orient=VERTICAL, command=logText.yview)
logText['yscroll'] = vscroll2.set
vscroll2.pack(side="right", fill="y")
logText.pack(side="left", fill="both", expand=True)

#Frame containing timer, labels for outputs, and output textbox with horizontal scroller
outputFrame = Frame(bottomFrame, borderwidth=10, bg = "white", relief="sunken", height = 360, width = 750)
outputFrame.pack(side = "top", fill = "both", expand = True)

nameLabel = Text(outputFrame,wrap = WORD, height = 19, width = 15, borderwidth=0)
nameLabel.tag_configure("right", justify='right')

#HardCoded Labels, might want to set index values like with output textbox
#nameLabel.insert(1.0, "\n\nSequence: \n\nPSI Pred: \nPSI Conf: \nPSS Pred: \nPSS Conf: \nJPred Pred: \nJPred Conf: \nRaptorX Pred: \nRaptorx Conf: \nYASPIN Pred: \nYASPIN Conf: \nSable Pred: \nSable Conf: \nSSPro Pred: \nSSPro Conf: \n\nMajority Vote: ")
nameLabel.insert(1.0, "\n\nSequence: \n\nPSI Pred: \nPSI Conf: \nPSS Pred: \nPSS Conf: \nJPred Pred: \nJPred Conf: \nRaptorX Pred: \nRaptorx Conf: \nYASPIN Pred: \nYASPIN Conf: \nSable Pred: \nSable Conf: \nSSPro Pred: \nSSPro Conf: \n\nMajority Vote: ")

#Align text to the right
nameLabel.tag_add("right", "1.0", "end")
nameLabel.configure(state='disabled')
nameLabel.pack(side = 'left', fill= "both") 

#Frame to hold output sequences and horizontal scrollbar
seqOutFrame = Frame(outputFrame, bg ="white")
outputText = Text(seqOutFrame, wrap = NONE, height = 22, borderwidth=0)
#colors for output color coding, used in colorCode()
outputText.tag_configure("Helix", foreground = "blue")
outputText.tag_configure("Strand", foreground = "green")
outputText.tag_configure("Coil", foreground = "red")

fillString()
outputText.configure(state='disabled')

hscroll = Scrollbar(seqOutFrame, orient=HORIZONTAL, command=outputText.xview)
outputText['xscroll'] = hscroll.set


outputText.pack(side="top", fill="x")
hscroll.pack(side="top", fill="x")
seqOutFrame.pack(side='left', fill="both", expand = True)
#Starting up
email_service = emailtools.login()
email_address = emailtools.getEmailAddress(email_service)
root.mainloop()

'''
	sequence length notes:
		RaptorX: 26 < x <= 4000
		JPred: 20 < x <= 800
		SSPro: x <= 400
		Yaspin: x <= 4000
		PSIPRED: 30 <= x <= 1500
		PSSPRED: x < 4000
		SABLE:  No limit? Sent 12000 length seq (and 300 requests/24hr)
	Ideal min length: 30
	Ideal max length: 800
'''
