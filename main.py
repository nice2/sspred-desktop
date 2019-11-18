from tkinter import *
import time
from services import ss, psi, jpred, raptorx, pss, sable, sspro, yaspin, emailtools, htmlmaker, batchtools
import threading

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
	if not seq or any(c not in 'ARNDCEQGHILKMFPSTWYV' for c in seq) or length < 40 or length > 4000:
		print('Invalid sequence: empty, contains invalid characters, or below 40/past 4000 in length')
	
	structId = ''
	chainId = ''
	pdbdata = None
	if structureIdEntry.get() and chainIdEntry.get():
		#print("Known sequence input given")
		structId = ''.join(structureIdEntry.get().split())
		chainId = ''.join(chainIdEntry.get().split())
		pdbdata = batchtools.pdbget(structId, chainId)
		#'''
		if pdbdata:
			seq = pdbdata['primary']
		#'''
	
	
	#Create list of selected sites
	selected = []
	for sites in siteCheckDict.keys():
		key = siteCheckDict[sites].get()
		if key:
			selected.append(siteDict[sites])
			print("Sending sequence to " + sites)

	startTime = batchtools.randBase62() #Time data was submitted
	ssObject = [] #List of completed sites
	
	#Create threads and send data
	for s in selected:
		mythread = threading.Thread(target = run, args = (s, seq, pdbdata, startTime, ssObject, len(selected)))
		mythread.setName(key)
		mythread.start()

#Takes data and sends it to a target site, then adds it to the ssObject list when completed
#Takes a site from siteDict, sequence, pdbdata dict, ssObject to place results in, and the number of selected sites (for knowing when all results are out)
def run(predService, seq, pdbdata, startTime, ssObject, target):

	tempSS = predService.get(seq, email)
	ssObject.append(tempSS)

	majority = None
	#Do majority vote and create html if successful
	if tempSS.status == 1 or tempSS.status == 3:
		majority = batchtools.majorityVote(seq, ssObject)

	htmlmaker.createHTML(startTime, ssObject, seq, pdbdata, majority)
	
	if len(ssObject) == target:
		print("All predictions completed.")
		#htmlmaker.createHTML(startTime, ssObject, seq, pdbdata, majority)
	'''
	#add to tkinter
	failList = []
	for obj in ssobj:
		if obj.status != 1 and obj.status != 3:
			failList.append(obj)
	
	if len(failList) >= 1:
		output += "<ul>Sites that failed to return a prediction:"
		for obj in failList:
			output += "<li>" + obj.name + "</li>"
		output += "</ul>"
	'''
	
root = Tk()
root.title("Secondary Structure Prediction Display")
root.geometry("800x600")

# Top Frame will contain sequence entry and control buttons
topFrame = Frame(root)
topFrame.pack(side='top')

# Bottom Frame will contain Outputs
bottomFrame = Frame(root)
bottomFrame.pack(side='top', fill ='both', expand = True)

#######Top Frame#######
#Contains sequence text box
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