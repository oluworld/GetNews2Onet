import string
import sys
from base64 import decodestring as base64_decodestring
from multifile import MultiFile
from rfc822 import Message

from AppWorks.Jobs.Job import Job
from etoffiutils import dumptextfile, false, true
from etoffiutils2.LineReader import LineReader


class MailExtractBase:
	def __init__(self, executor):
		self.executor = executor
	
	def translate_message(self, ll, dn, filename):
		assert false
	
	def add_newsgroup_message(self, uniqifier, spectionary, f1, f2):
		jj = Job('foo-' + uniqifier, len(spectionary.keys()), spectionary, 'direct-invocation', (f2, f1))
		o = self.executor.execute(jj)


class MailExtractNull(MailExtractBase):
	def go(self, dn, each, cur, first, last):
		# print "** Null Format - either empty or yenc or directory"
		raise WrongFormat()

	def extract_srv_info(self, ll, dn, filename):
		""" @returns server, group, msgnum, f1, f2"""
		#raise NullMessage, "Can't extract null message"
		print >>sys.stderr, "Can't extract null message"


class EmlF1(object):
	def __init__(self, f1):
		x = string.split(f1, '\n')
		self.f1 = filter(lambda x: x != '', x)
	
	def set_properties(self, onet_obj):
		def split_on_colon(s):
			n, v = string.split(s, ':', 1)
			n = n.strip()
			v = v.strip()
			return n, v
		
		assert self.f1[0][0] == '/'
		x = [split_on_colon(y) for y in self.f1[1:]]
		[onet_obj.set_prop(n, v) for (n, v) in x]


class CBracketF1(object):
	def __init__(self, f1):
		self.f1 = f1
		
	def set_properties(self, onet_obj):
		def split_on_equals(s):
			n, v = string.split(s, '=', 1)
			n = n.strip()
			v = v.strip()
			return n, v
		
		x = [split_on_equals(y) for y in self.f1]
		[onet_obj.set_prop(n, v) for (n, v) in x]


class MailExtractEML(MailExtractBase):
	def extract_srv_info(self, ll, dn, cur):
		try:
			lr = LineReader(ll)
			msg = Message(lr)
			
			subj = msg.getheader("subject")
			#	print 67, msg.headers
			#	qq = string.split(subj)
			if subj is None:
				raise WrongFormat
			
			# decode subject
			server, group, msgnum, f1, f2, qq = self.decode_subject(subj, lr)
			
			# decode message
			##	print 99, f1, f2
			assert f1 != []
			assert f2 != []
			f1 = base64_decodestring(string.join(f1))
			f2 = string.split(base64_decodestring(string.join(f2, '\n')), '\n')
			
			return server, group, int(msgnum), EmlF1(f1), f2
		finally:
			del lr, msg
	
	def decode_subject(self, subj, lr):
		""" """
		if subj[0] == '/':
			qq = subj.split('/')
			server = qq[2]
			group = qq[3]
			msgnum = qq[4]
			
			mfi = MultiFile(lr, 0)
			mfi.next()
			f1 = mfi.readlines()
			mfi.next()
			f2 = mfi.readlines()
		else:
			qq = subj.split()
			server = qq[4]
			group = qq[2]
			msgnum = qq[0]
			
			mfi = MultiFile(lr, 0)
			mfi.next()
			mfi.next()
			f1 = mfi.readlines()
			mfi.next()
			f2 = mfi.readlines()
		
		del mfi
		
		return server, group, msgnum, f1, f2, qq


class MailExtractCBracket(MailExtractBase):
	def extract_srv_info(self, ll, dn, msgnum):
		# this function actually depends on a numeric filename
		if not msgnum[-4:].lower() == ".{c}":
			return
		
		assert is_integer(msgnum[:-4])
		try:
			lr = LineReader(ll)
			msg = Message(lr)
			
			xref = msg.getheader("xref")
			xxr = xref.split(' ')
			server = xxr[0]
			pgroups = map(lambda x: x.split(':'), xxr[1:])
			# ~ print '** pgroups', pgroups
			msgnum = int(msgnum[:-4])
			group_name = ''
			for x, y in pgroups:
				# print 88, x, y
				if int(y) == msgnum:
					group_name = x
					break
			MM = '%s/%s' % (dn, msgnum)
			f1 = dumptextfile(MM + '.{M}')
			f2 = ll  # dumptextfile(MM+'.{C}')
			
			return server, group_name, msgnum, CBracketF1(f1), f2
		finally:
			del lr, msg


class WrongFormat(Exception): pass


def is_integer(s):
	for each in s:
		if each not in "1234567890":
			return false
	return true
