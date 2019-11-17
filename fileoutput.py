import time
import os
import webbrowser

#Creates folder in running directory using "pred month.day.year hr.min.sec" as the name (based off startTime)
def createFolder(startTime):
	nameFormat = getNameFormat(startTime)
	try:
		os.mkdir(os.getcwd() + "/" + nameFormat);
	except OSError:
		print ("Folder " + nameFormat + " already exists.")
	else:
		print("Created folder " + nameFormat + " to save output to.")

#Saves the output to a txt file. Takes a startTime for naming, ssList for the heading, and ssObject for the outputs
#"pred month.day.year hr.min.sec" for file name
def createTxt(startTime, ssList, ssObject):
	
	nameFormat = getNameFormat(startTime)
	filePath = os.path.join(os.getcwd() + "/" + nameFormat, "pred " + nameFormat + ".txt")
	file = open(filePath, "w+")
	
	output = ''
	output += ssList[0].replace("\n", "".rjust(14)) + "\n"
	output += "Sequence:".rjust(14) + ssList[1] + "\n"
	
	for i in ssObject:
		if i.status == 1:
			output+=i.plabel.rjust(14) + i.pred+ "\n"
			output+=i.clabel.rjust(14) + i.conf+ "\n"
	output += "\nMajority Vote:" + ssList[-1]
	'''		
	output += "\n\n"
	
	#Show services with errors at bottom
	for i in ssObject:
		if i.status == 2:
			output+=i.plabel + i.pred+ "\n"
			output+=i.clabel + i.conf+ "\n"
	'''
	file.write(output)

#Saves the output to an HTML file. Takes a startTime for naming, ssList for the heading, and ssObject for the outputs
#"pred month.day.year hr.min.sec" for file name
#Opens this file upon completion (into a new tab if possible)
def createHTML(startTime, ssList, ssObject):
	nameFormat = getNameFormat(startTime)
	filePath = os.path.join(os.getcwd() + "/" + nameFormat, "pred " + nameFormat + ".html")
	file = open(filePath, "w+")
	
	#Replace spaces with &nbsp; in order to get them to show
	output = "<!DOCTYPE html><html><body style='font-family:monospace;'>" #use monospace as font to have equal spacing between all characters
	output += "<div>" + (ssList[0].replace("\n", "".rjust(14))).replace(" ", "&nbsp;") + "</div>"
	output += "<div>" + ("Sequence:".rjust(14) + ssList[1]).replace(" ", "&nbsp;") + "</div>"
	for i in ssObject:
		if i.status == 1:
			output+="<div>" + ((i.plabel).rjust(14)).replace(" ", "&nbsp;") #prediction source
			preds = i.pred #prediction results to be colored
			for c in preds:
				output += "<span style='color:" + getColor(c) + "';>" + c + "</span>"
			output += "</div>"
			output += "<div>" + ((i.clabel).rjust(14)).replace(" ", "&nbsp;") + i.conf + "</div>"
	
	output += "<div>Majority Vote:"
	for c in ssList[-1]:
		output += "<span style='color:" + getColor(c) + "';>" + c + "</span>"
	output += "</div></body></html>"
	file.write(output)
	
	url = "file://" + filePath
	webbrowser.open(url,new = 2) #new 2 for new tab

#Takes a character and returns the color it should be represented as
#Helix = blue, Strand = green, Coil = red
def getColor(character):
	if character == 'H':
		return "blue"
	elif character == 'E':
		return "green"
	elif character == 'C':
		return "red"
	
	return "black"
	
#Takes a start time and returns a format for file naming
def getNameFormat(startTime):
	return time.strftime("%m.%d.%Y %H.%M.%S",time.localtime(startTime))
	
