from tkinter import *
import pyperclip

#Tkinter widget classes

#Text with right clicking and scrolling
class ProperText(Frame):
	
	textField = None
	rightClickMenu = None
	
	def __init__(self, frame, height=None, width=None):
		Frame.__init__(self, frame, borderwidth=1, relief="sunken")
		
		self.textField = Text(self, height=height, width=width, wrap = CHAR, borderwidth=0)
		self.textField.pack(side="left", fill="both", expand=True)
		vscroll = Scrollbar(self, orient=VERTICAL, command=self.textField.yview)
		self.textField['yscroll'] = vscroll.set
		vscroll.pack(side="right", fill="y")
		self.rightClickMenu = Menu(self.textField, tearoff = 0)
		self.rightClickMenu.add_command(label="Copy", command=self.copy)
		self.rightClickMenu.add_command(label="Paste", command=self.paste)
		
		self.textField.bind("<Button-3>", self.popupmenu)
		
		#Used to call/access text members
		self.get = self.textField.get
		self.insert = self.textField.insert
		self.delete = self.textField.delete
		self.mark_set = self.textField.mark_set
		self.index = self.textField.index
		self.search = self.textField.search
		self.see = self.textField.see
		
		#Can also be used to call the above functions. Meant for accessing the text widget itself, such as text['state']
		self.text = self.textField

	def popupmenu(self, event):
		try:
			self.rightClickMenu.tk_popup(event.x_root, event.y_root, 0)
		finally:
			self.rightClickMenu.grab_release()
	
	#Copies selected text
	def copy(self):
		try:
			pyperclip.copy(self.selection_get())
		except:
			print("No selection")
	
	#Paste only in editable fields
	def paste(self):
		if self.textField['state'] != 'disabled':
			text = pyperclip.paste() #store paste
			index = self.index(INSERT) #get the current position as index
			
			#If there is a selected range, delete it and use the first index as the new index
			try:
				self.delete(SEL_FIRST, SEL_LAST)
				index = self.index(SEL_FIRST)
			except:
				print("No selection")
			self.insert(index, text)

#Entry with right clicking
class ProperEntry(Entry):

	rightClickMenu = None
	
	def __init__(self, parent, width=None):
		Entry.__init__(self, parent, width=width)
		
		self.rightClickMenu = Menu(self, tearoff = 0)
		self.rightClickMenu.add_command(label="Copy", command=self.copy)
		self.rightClickMenu.add_command(label="Paste", command=self.paste)
		
		self.bind("<Button-3>", self.popupmenu)

	def popupmenu(self, event):
		try:
			self.rightClickMenu.tk_popup(event.x_root, event.y_root, 0)
		finally:
			self.rightClickMenu.grab_release()

	def copy(self):
		try:
			pyperclip.copy(self.selection_get())
		except:
			print("No selection")
		
	def paste(self):
		text = pyperclip.paste() #store paste
		index = self.index(INSERT) #get the current position as index
		
		#If there is a selected range, delete it and use the first index as the new index
		try:
			self.delete(SEL_FIRST, SEL_LAST)
			index = self.index(SEL_FIRST)
		except:
			print("No selection")
		
		self.insert(index, text)