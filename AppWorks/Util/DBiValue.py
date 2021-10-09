#from AwxObject import *
from etoffiutils import true, false

class AwxAccess:
	NoAccess = 0
	Read = 1
	Write = 2
	ReadWrite = 3

class DBiValue:
	def __init__(self, path, value, owner, extra, \
				expires = None, refresh = None, \
				Access = AwxAccess.ReadWrite,  \
				dirty  = false, syncable = true):
		self.path = path
		self.value = value
		self.owner = owner
		self.extra = extra
		self.Access = Access
		self.dirty = dirty
		self.syncable = syncable
		self.expires = expires
		self.refresh = refresh
	
	def getStr(self):
##		print 'YY',self.value
		return self.value
	
	def getInt(self):
		import string
		return string.atoi(self.value)
	
	def getBool(self):
		if self.value in ('1', 'yes', 'true'):
			return true
		if self.value in ('0', 'no', 'false'):
			return false
		return TypeError()
	
	def getPath(self):
		return self.path

	def getName (self):
		def strsplit(instr, splitby):
			pos = instr.rfind(splitby)
			return instr[:pos], instr[pos+1:]
		
		x1, x2 = strsplit(self.path, '/')
		return x2
		
	def __repr__(self):
		return '<DBiValue %s=%s %s %s>' % (self.path, self.value, self.owner, self.extra)

#eof
