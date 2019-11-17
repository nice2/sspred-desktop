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
		self.plabel = name.rjust(7) + " Pred:"
		self.clabel = name.rjust(7) + " Conf:"
		self.pred = ""
		self.conf = ""
		self.cconf = []
		self.hconf = []
		self.econf = []
		self.status = 0
	
	'''
		Statuses:
			0 = not finished
			1 = finished
			2 = ended with error
	'''
	