from AppWorks.Services.AwxDBiServer import DBiServer

class AwxDBi:
	EnumFlat = 0
	EnumRecursive = 1
		
	def enum(self, Key, kind = EnumRecursive):
##		if root == None:
##			root = self.root
		rv = DBiServer.enum(Key, self.root, kind)
##		print '//88// %s' % rv
		return rv
		
	def getStrWithDefault(self, Key, default):
		try:
			rv = self.getStr(Key)
		except KeyError: ## RCDBiHandle.getValue
			rv = default
		return rv
	def getStr(self, Key):
##		print '%% getStr(%s %s)' % (self.root, Key)
		rv = DBiServer.getStr(Key, self.root)
##		import sys, traceback
##		traceback.print_stack()#file=sys.stdout)
##		print '%% getStr RETURNS -> %s' % rv
		return rv 
		
	def setRoot(self, root):
##		print 'new root is %s' % root
		self.root = root
		
	def __init__(self, root='/local/DBi/'):
		self.values = {}
		self.setRoot(root)
		
#eof
