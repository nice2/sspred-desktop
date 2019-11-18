import time
import os
import json

#Displays character position 
def drawCounter(mySeq):
	j=0
	p = 1
	#counterstr = 15*'&nbsp;'
	counterstr = ''
	while j < len(mySeq):
		if j%10 != 0:
			counterstr += ' '
			j = j+1
		else:
			for k in range(len(str(p))):
				counterstr += str(str(p)[k])
				j=j+1
			p = p+10
	
	return counterstr

#Writes the output to an HTML file. 
#Takes a startTime string,ssObject,seq, and optional structid/chainid and majority vote for the outputs
#startTime for file name
#Splits outputs into lines of length depending on the rowlength parameter + 15
def createHTML(startTime, ssobj, seq, pdbdata = None, majority = None, hColor = "blue", eColor = "green", cColor = "red", rowlength = 60):
	
	output = ''
	
	#Add template
	with open(os.path.join(os.getcwd() + "/output/static/template.html"), "r") as custom:
		for line in custom:
			output += line

	#Create script tag containing data
	output += "<script type='text/javascript'>"
	
	dictArray = []
	
	dictArray.append({'sequence' : seq})
	
	for obj in ssobj:
		#print(vars(obj))
		dictArray.append(vars(obj))

	if pdbdata:
		dictArray.append(pdbdata)
	if majority:
		dictArray.append({'majority' : majority})
		
	output += "var a = "
	output += json.dumps(dictArray) + ";"
	output += "</script>"
	
	#Close off template
	output += "</html>"
	
	#Write to file
	filePath = os.path.join(os.getcwd() + "/output/" + startTime + ".html")
	file = open(filePath, "w+")
	file.write(output)
	
	'''
	#auto open results
	url = "file://" + filePath
	webbrowser.open(url,new = 2) #new 2 for new tab
	'''
	#return output

#Takes a character and 3 optional colors. Returns the color it should be represented as
#Default: Helix = blue, Strand = green, Coil = red
def getColor(character, hColor = "blue", eColor = "green", cColor = "red"):
	if character == 'H':
		return hColor
	elif character == 'E':
		return eColor
	elif character == 'C':
		return cColor
	
	return "black"