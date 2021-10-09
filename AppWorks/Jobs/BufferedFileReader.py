class FileReader:
	def __init__ (self):
		self.backed = None
		self.at_end = 0
	def open (self, name):
		self.name = name
		self.fo = open (name, 'r')
	def readlines (self):
		return self.fo.readlines()
	def readline (self):
#		print 'in readine'
#		print '--------------'
#		print 'backed=', self.backed
#		print 'at_end=', self.at_end
#		print '--------------'
		if self.at_end == 1:
			raise Foo()
		if self.backed != None:
			t = self.backed
			self.backed = self.fo.readline()
#			print 'just read line', self.backed
			if self.backed in (None, ''):
				self.at_end = 1
#			print 'returning =', t
			return t
		else:
			t = self.fo.readline()
			self.backed = self.fo.readline()
#			print 'returning =', t
			return t
	def close(self):
		return self.fo.close()
class Foo (Exception):
	def __str__(self):
		return "hello from foo"
#	pass
