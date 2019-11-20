from tkinter import *
import time
from services import ss, psi, jpred, raptorx, pss, sable, sspro, yaspin, emailtools, htmlmaker, batchtools
import threading
import os
import webbrowser

#Dictionary containing sites and their classes
siteDict = {
	"JPred": jpred,
	"PSI": psi,
	"PSS": pss,
	"RaptorX": raptorx,
	"Sable": sable,
	"Yaspin": yaspin,
	"SSPro": sspro
}

#Login to email account to be able to send emails
email_service = emailtools.login()
email = emailtools.getEmailAddress(email_service)

#Verifies input and starts threads to send to selected sites
def sendData():
	seq = (''.join(seqText.get(1.0,END).split())).upper()
	
	length = len(seq)
	validated = True
	log = statusText.get(1.0, 'end-1l')
	#Validate Seq
	if not seq or any(c not in 'ARNDCEQGHILKMFPSTWYV' for c in seq) or length < 40 or length > 4000:
		#print('Invalid sequence: empty, contains invalid characters, or below 40/past 4000 in length')
		log += '-Invalid sequence: empty, contains invalid characters, or below 40/past 4000 in length \n'
		validated = False
	
	#Validate sites
	selected = [] #Create list of selected sites
	for sites in siteCheckDict.keys():
		key = siteCheckDict[sites].get()
		if key:
			selected.append(sites)
	if not selected:
		#print('No sites selected')
		log += '-No sites selected \n'
		validated = False
		
	structId = ''
	chainId = ''
	pdbdata = None #Store pdbdata if it exists
	if structureIdEntry.get() and chainIdEntry.get() and len(structureIdEntry.get()) >= 4:
		#print("Known sequence input given")
		structId = ''.join(structureIdEntry.get().split())
		chainId = ''.join(chainIdEntry.get().split())
		pdbdata = batchtools.pdbget(structId, chainId)
		if pdbdata:
			seq = pdbdata['primary']
		else:
			validated = False
			log += '-Invalid structure id or chain Id \n'
			#print('Invalid structure id or chain Id')

	if validated:
		#Disable input if all inputs allowed
		disableInput()
		
		unformattedStartTime = time.time()	 #Time data was submitted
		startTime = batchtools.randBase62(unformattedStartTime)
		ssObject = [] #List of completed sites
		
		#Let open results button know which file to look for
		openButton['command'] = lambda: openResults(startTime)
		
		#Start time elapsed counter
		timeElapse(unformattedStartTime, ssObject, len(selected))
		
		#Create threads and send data
		for s in selected:
			log += "-Sending sequence to " + s + ".\n"
			updateText(statusText, log)
			mythread = threading.Thread(target = run, args = (siteDict[s], seq, pdbdata, startTime, ssObject, len(selected)))
			mythread.setName(key)
			mythread.start()
	else:
		updateText(statusText, log)

#Takes data and sends it to a target site, then adds it to the ssObject list when completed
#Takes a site from siteDict, sequence, pdbdata dict, ssObject to place results in, and the number of selected sites (for knowing when all results are out)
def run(predService, seq, pdbdata, startTime, ssObject, target):
	tempSS = predService.get(seq, email)
	ssObject.append(tempSS)

	majority = None
	#Do majority vote and create html if successful
	if tempSS.status == 1 or tempSS.status == 3:
		majority = batchtools.majorityVote(seq, ssObject)
	
	log = statusText.get(1.0, 'end-1l')
	log += "-" + tempSS.name + " " + ss.statusDict[tempSS.status] + "\n"
	if tempSS.status != 1 and tempSS.status != 3:
		log +=  "-" + tempSS.pred + "\n" #Print reason for failure
	
	htmlmaker.createHTML(startTime, ssObject, seq, pdbdata, majority)
	openButton['state'] = 'normal'
	
	if len(ssObject) == target:
		#print("All predictions completed.")
		log += "-All predictions completed. \n"
		enableInput()
	updateText(statusText, log)

#Updates every second to display time elapsed
def timeElapse(startTime, ssObject, target):
	if len(ssObject) != target:
		currentTime = time.strftime("%H:%M:%S", time.gmtime(time.time()-startTime))
		timeElapsed = "Time Elapsed: " + currentTime
		timeElapsedLabel.config(text = timeElapsed)
		root.after(1000, lambda: timeElapse(startTime, ssObject, target))
	
#Opens the html file with the same name as startTime
def openResults(startTime):
	#print(startTime)
	url = "file://" + os.path.join(os.getcwd() + "/output/" + startTime + ".html")
	webbrowser.open(url,new = 2) #new 2 for new tab

#Disables any buttons/fields to prevent any more input when running
def disableInput():
	startButton['state'] = 'disabled'
	clearButton['state'] = 'disabled'
	seqText['state'] = 'disabled'
	
	jpredCheck.config(state=DISABLED)
	psiCheck.config(state=DISABLED)
	pssCheck.config(state=DISABLED)
	raptorxCheck.config(state=DISABLED)
	sableCheck.config(state=DISABLED)
	yaspinCheck.config(state=DISABLED)
	ssproCheck.config(state=DISABLED)
	
	structureIdEntry.config(state=DISABLED)
	chainIdEntry.config(state=DISABLED)
	
	openButton['state'] = 'disabled' #Will be reenabled when output is made
	
#Enables input options so that another sequence can be made
def enableInput():
	startButton['state'] = 'normal'
	clearButton['state'] = 'normal'
	seqText['state'] = 'normal'
	
	jpredCheck.config(state=NORMAL)
	psiCheck.config(state=NORMAL)
	pssCheck.config(state=NORMAL)
	raptorxCheck.config(state=NORMAL)
	sableCheck.config(state=NORMAL)
	yaspinCheck.config(state=NORMAL)
	ssproCheck.config(state=NORMAL)
	
	structureIdEntry.config(state=NORMAL)
	chainIdEntry.config(state=NORMAL)

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
	textbox.see(END) #Scroll to bottom

root = Tk()
root.title("Secondary Structure Prediction Display")
root.geometry("800x600")

# Top Frame will contain sequence entry and control buttons
topFrame = Frame(root)
topFrame.pack(side='top')

# Bottom Frame will contain prediction statuses
bottomFrame = Frame(root)
bottomFrame.pack(side='top')

#######Top Frame#######

#Contains sequence text box -----------------------needs right clicking
seqFrame = Frame(topFrame)
seqLabel = Label(seqFrame, text="Sequence: ")
seqLabel.grid(row=0, column=0, sticky=W)
seqTextFrame = Frame(seqFrame,borderwidth=1, relief="sunken")
seqTextFrame.grid(row=1, column=0, sticky=W)
seqText = Text(seqTextFrame, wrap = CHAR, height = 5, width = 30, borderwidth=0)
vscroll = Scrollbar(seqTextFrame, orient=VERTICAL, command=seqText.yview)
seqText['yscroll'] = vscroll.set
vscroll.pack(side="right", fill="y")
seqText.pack(side="left", fill="both", expand=True)
clearButton = Button(seqFrame, text="Clear Sequence", command = lambda: updateText(seqText, '')) #Clears seqText
clearButton.grid(row = 2, column = 0, pady=5)

#Contains checkboxes to select sites
sitesFrame = Frame(topFrame)
sendToLabel = Label(sitesFrame, text="Send to:")
sendToLabel.grid(row=0, column=0, sticky=W)

#Checkboxes and their variables for determining state
jpredVar = IntVar()
psiVar = IntVar()
pssVar = IntVar()
raptorxVar = IntVar()
sableVar = IntVar()
yaspinVar = IntVar()
ssproVar = IntVar()
jpredCheck = Checkbutton(sitesFrame, text="JPred", variable=jpredVar)
psiCheck = Checkbutton(sitesFrame, text="PSIPred", variable=psiVar)
pssCheck = Checkbutton(sitesFrame, text="PSSPred", variable=pssVar)
raptorxCheck = Checkbutton(sitesFrame, text="RaptorX", variable=raptorxVar)
sableCheck = Checkbutton(sitesFrame, text="SABLE", variable=sableVar)
yaspinCheck = Checkbutton(sitesFrame, text="YASPIN", variable=yaspinVar)
ssproCheck = Checkbutton(sitesFrame, text="SSPRO", variable=ssproVar)
siteCheckDict = {
	"JPred": jpredVar,
	"PSI": psiVar,
	"PSS": pssVar,
	"RaptorX": raptorxVar,
	"Sable": sableVar,
	"Yaspin": yaspinVar,
	"SSPro": ssproVar
}
jpredCheck.grid(row=1, column=0, sticky=W)
psiCheck.grid(row=1, column=1, sticky=W)
pssCheck.grid(row=1, column=2, sticky=W)
raptorxCheck.grid(row=2, column=0, sticky=W)
sableCheck.grid(row=2, column=1, sticky=W)
yaspinCheck .grid(row=2, column=2, sticky=W)
ssproCheck.grid(row=3, column=0, sticky=W)

#Contains input for if the sequence is known
knownSeqFrame = Frame(topFrame, pady=10)
knownSeqLabel = Label(knownSeqFrame, text="Known Sequence:")
knownSeqLabel.grid(row=0, column=0, sticky=W)
structureIdLabel = Label(knownSeqFrame, text="Structure Id:")
structureIdLabel.grid(row=1, column=0, sticky=W)
structureIdEntry = Entry(knownSeqFrame)
structureIdEntry.grid(row=1, column=1, sticky=W)
chainIdLabel = Label(knownSeqFrame, text="Chain Id:")
chainIdLabel.grid(row=2, column=0, sticky=W)
chainIdEntry = Entry(knownSeqFrame)
chainIdEntry.grid(row=2, column=1, sticky=W)

#Input buttons
controlFrame = Frame(topFrame)
startButton = Button(controlFrame, text="Start", command = sendData) #Button to start sendData function
startButton.grid(row = 0, column = 0, padx=10)

#Time elapsed label
timeElapsedLabel = Label(topFrame, text="Time Elapsed: 00:00:00")

#Gridding the main parts of the top frame
seqFrame.grid(row=0, column=0, sticky=W)
sitesFrame.grid(row=1, column=0, sticky=W)
knownSeqFrame.grid(row=2, column=0, sticky=W)
controlFrame.grid(row=3, column=0)
timeElapsedLabel.grid(row = 4, column = 0)

#Status box
statusFrame = Frame(bottomFrame)
statusLabel = Label(statusFrame, text="Prediction Status:")
statusLabel.grid(row=0, column=0, sticky=W)
statusTextFrame = Frame(statusFrame,borderwidth=1, relief="sunken")
statusTextFrame.grid(row=1, column=0, sticky=W)
statusText = Text(statusTextFrame, wrap = CHAR, height = 10, width = 50, borderwidth=0)
statusText['state'] = 'disabled' #Disable writing to status box
vscroll2 = Scrollbar(statusTextFrame, orient=VERTICAL, command=statusText.yview)
statusText['yscroll'] = vscroll2.set
vscroll2.pack(side="right", fill="y")
statusText.pack(side="left", fill="both", expand=True)

#Open results buttons
openButton = Button(bottomFrame, text="Open Results")
openButton['state'] = 'disabled'

#Gridding the main parts of the bottom frame
statusFrame.grid(row = 0, column = 0, sticky=N)
openButton.grid(row = 1, column = 0, pady=10)

#Check all sites by default
psiCheck.select()
raptorxCheck.select()
sableCheck.select()
yaspinCheck.select()
ssproCheck.select()
jpredCheck.select()
pssCheck.select()
ssproCheck.select()

root.mainloop()