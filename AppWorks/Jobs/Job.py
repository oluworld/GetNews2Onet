from etoffiutils2.text import SplitLine, getQuoted

class Job:
	def __init__ (self, id, nspec, specl, type, k):
		self.set (id, nspec, specl, type, k)

	def set (self, id, nspec, specl, type, k):
		self.id = id
		self.nspec = nspec
		self.spec_list = specl
		self.job_type = type
		self.params = k

	def read_from_ascii_file (self, jfi):
		(id, nspec, specl, type, k) = ('', 0, {}, '', [])
		try:
			l = jfi.readline()[:-1]
			if l == '%%':
				l = jfi.readline()[:-1]
		
			id = l
			type = jfi.readline()[:-1]
			nspec = int( jfi.readline()[:-1] )
			# SPECS: Depends-On, Priority, System-Load
			for each in range(0, nspec):
				l = jfi.readline()[:-1]
				n, v = SplitLine(l)
				specl[n] = v
			k = []
			l = jfi.readline()[:-1]
			while l != '%%':
				k.append( l )
				l = jfi.readline()[:-1]
			self.set(id, nspec, specl, type, k)
		except IOError, e:
			return 0
		return 1
