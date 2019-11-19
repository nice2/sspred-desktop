class SS:
	def __init__(self, name, pred, conf, cconf, hconf, econf):
		self.name = name
		self.pred = pred
		self.conf = conf
		self.cconf = cconf
		self.hconf = hconf
		self.econf = econf
		self.status = 0
		
	def __init__(self, name):
		self.name = name
		self.plabel = name.rjust(8) + " Pred:"
		self.clabel = name.rjust(8) + " Conf:"
		self.pred = ""
		self.conf = ""
		self.cconf = []
		self.hconf = []
		self.econf = []
		self.status = 0
	
statusDict = ["not finished", "finished", "ended with an error", "finished (does not provide conf)"]
	
'''
	Statuses:
		0 = not finished
		1 = finished
		2 = ended with error
		3 = finished with no conf
'''
	