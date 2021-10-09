from AppWorks.Util.DBiValue import *
from etoffiutils import xstat, progressiveParse, \
	true, false, checkRemoveEnd
from etoffiutils2.text import SplitLine, getQuoted
import string

DBiServer = None

class RCDBiHandler:
	RCEXT = '.rc'
	RCSIG = None

	def __init__(self, srv):
		self._files = {}
		self.locked = false
		global DBiServer
		DBiServer = srv
	def Begin(self, root):
		# Begin(root:STRING)->None
		try:
			root=checkRemoveEnd(root,'/')
			if not self._files.has_key(root):
				self._files[root] = {}
				self._files[root]['max'] = 0

				self._Begin(root) # the real worker bee
		except IOError, e:
			print e
	def getValue(self, path):
		rv = None
		u = progressiveParse(path, '/')[1:-3]
		for each in u:
			each = each[:-1] #checkRemoveEnd(each, '/')
			fn   = self.GetFileName(each)
			if xstat(fn):
				self.lock()
				self.Begin(each)
				rv = self.locker[path]
				self.unlock()
				break
		return rv
	def canOpen(self, root, Type):
		u = progressiveParse(root, '/')[:-2]
		if Type == DBiServer.FOR_GET:
			u = u[1:]
		for each in u:
			each = checkRemoveEnd(each, '/')
			fn   = self.GetFileName(each)
##			print 'EACH '+each
##			print 'STAT '+fn
			if xstat(fn): 
				return true
		return false
	def getFileObj(self, filename_):
		""" return an object that supports `readline' """
		## TODO: this function is capable of opening *any* file on a system!!!
		fn = self.GetFileName(filename_)
		rv = open(fn, 'r')
		
##		print '%% (RCDBiHandler::_Begin) -> (%s)==(%s)' % (filename_, fn)
		
		if rv:
			if RCDBiHandler.RCSIG:
				if rv.readline() != RCDBiHandler.RCSIG:
					if rv.readline() != RCDBiHandler.RCSIG:
						rv = None
		return rv
	def _Begin(self, root):
		s       = self.getFileObj(root)
		linenum = 0 # one based!!!
		
		if s == None:
			return
		try:
			while 1:
				line = s.readline()
				if not line: s.close(); break
				linenum = linenum + 1
				if len(line)<2 or line[0] == '#':
##					print 'skipping ', line,
					continue
		
##				if line[:-1] == '\\':
##					line[:-1] = ''
##					linenum = linenum - 1
##					continue
		
				(name, value) = SplitLine(line[:-1])
		
				newval = DBiValue(root+'/'+name, value, self, (root, linenum))
				self._files[root][linenum]=newval
				self._files[root]['max']=max(self._files[root]['max'], linenum)
				self.__notifyNewValue(newval)
		finally:
			s.close()
			
	def End(self, root):
		print "ending ********************************", root
		R=self._files[root]
		F=self.GetOutFile(root)
		for each in xrange(1, self._files[root]['max']+1):
			L=R[each]
			L_name=L.path[string.rindex(L.path, '/')+1:]
			for each in (' ', '\n', '\r', '\t', "'", '=', '"'):
				if each in L_name:
					if each == '"':
						L_name = "'%s'" % L_name
					else:
						L_name = '"%s"' % L_name
					break
			F.write('%s %s\012' % (L_name, L.value))
		R=None
#		self._files.remove(root)
		del self._files[root]
	def __del__ (self):
		print "deleting"
		for each in self._files.keys():
			self.End (each)
	def __add_to_locker(self, value):
		if self.locked:
			self.locker[value.path]=value
	def __notifyNewValue(self, newval):
		global DBiServer
		DBiServer.add(newval)
		self.__add_to_locker(newval)
	def lock(self):
		self.locker={}
		self.locked=true
	def unlock(self):
		self.locker={}
		self.locked=false
	def __repr__(self):
		return '<RCDBiHandler >'
	def GetOutFile(self, root, mode='wb'):
		return open(self.GetFileName(root), mode)
	def GetFileName(self, root):
		if root[:2] == '~/':
			Root = "%s%s%s" % (DBiServer.DBIROOT, root[2:], self.RCEXT)
		elif root[:11] == '/local/DBi/':
			Root = "%s%s%s" % (DBiServer.DBIROOT, root[11:], self.RCEXT)
		else:
			Root = '%s%s' % (root, self.RCEXT)
		return Root

#eof
