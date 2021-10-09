import os, sys, time, string
from etoffiutils import dumptextfile, true, false
from rfc822 import Message
from multifile import MultiFile
from AppWorks.Jobs.Job import Job
from AppWorks.Invocation.OnetAddNewsgroupMessage import Onet_EmptyMessage, OANM1_JOB_EXECUTOR
from base64 import decodestring as base64_decodestring
from etoffiutils2.LineReader import LineReader
from etoffiutils2.OpMeasure import OpMeasure
from etoffiutils2.pkg import tt, ttp, combine_lists, xpmt, xmpta

class WrongFormat(Exception): pass
class pException(Exception): pass

def is_integer(s):
	for each in s:
		if each not in "1234567890":
			return false
	return true

class MailExtractMultiplexer:
	def __init__(self):
		self.executor = OANM1_JOB_EXECUTOR(None)
		self._eml=MailExtractEML(self.executor)
		self._cbr=MailExtractCBracket(self.executor)
		self._nul=MailExtractNull(self.executor)
	def get(self, filename):
		if filename[-4:]=='.eml':
			return self._eml
		elif filename[-4:]=='.{C}':
			return self._cbr
		else:
			return self._nul

class MailExtractBase:
	def __init__(self, executor):
		self.executor = executor
	def translate_message(self, ll, dn, filename):
		assert false
	def add_newsgroup_message (self, uniqifier, spectionary, f1, f2):
		jj = Job ('foo-'+uniqifier, len(spectionary.keys()), spectionary, 'direct-invocation', (f2, f1))
		o = self.executor.execute(jj)

class GetNews2Onet:
	def __init__(self):
		self.mem = MailExtractMultiplexer()
	def do_file(self, dirname, filename):
		fullname = '%s/%s' % (dirname, filename)
		try:
			ll = dumptextfile (fullname, true)
			self.translate_message (ll, dirname, filename)
			os.unlink (fullname)
		except WrongFormat, e:
			print '** wrong format'
		except Onet_EmptyMessage, e:
#			print e
			print '** Message is empty'
		except IOError, e:
			print '== Error Decoding', each
			print '\t', e
			print '================='
	def translate_message(self, ll, dn, filename):
		extractor = self.mem.get(filename)
		server, group, msgnum, f1, f2 = extractor.extract_srv_info(ll, dn, filename)
		
		# generate spectionary
		spectionary = {}
		spectionary['server']     = server
		spectionary['group_name'] = group
		spectionary['msgnum']     = msgnum
		spectionary['options']    = 'save-headers extract-contents-in-shared delete-orig'
		
		# invoke message adding component
		extractor.add_newsgroup_message(time.ctime(time.time()), spectionary, f1, f2)


class MailExtractNull(MailExtractBase):
	def go(self, dn, each, cur, first, last):
		#print "** Null Format - either empty or yenc or directory"
		raise WrongFormat()

class MailExtractEML(MailExtractBase):
	def extract_srv_info(self, ll, dn, cur):
		try:
			lr  = LineReader (ll)
			msg = Message (lr)
			
			subj = msg.getheader("subject")
			#	print 67, msg.headers
			#	qq = string.split(subj)
			if subj is None:
				raise WrongFormat
		
			# decode subject
			server, group, msgnum, f1, f2, qq = self.decode_subject (subj, lr)
			
			# decode message
		##	print 99, f1, f2	
			assert f1 != []
			assert f2 != []
			f1 = base64_decodestring (string.join(f1))
			f2 = string.split(base64_decodestring (string.join(f2,'\n')), '\n')
			
			return server, group, msgnum, f1, f2
		finally:
			del lr, msg
	def decode_subject (self, subj, lr):
		""" """
		if subj[0] == '/':
			qq = subj.split('/')
			server = qq[2]
			group  = qq[3]
			msgnum = qq[4]
	
			mfi = MultiFile (lr, 0)
			mfi.next () 
			f1 = mfi.readlines()
			mfi.next () 
			f2 = mfi.readlines()
		else:	
			qq = subj.split()	
			server = qq[4]
			group  = qq[2]
			msgnum = qq[0]
		
			mfi = MultiFile (lr, 0)
			mfi.next () 
			mfi.next () 
			f1 = mfi.readlines()
			mfi.next ()
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
			lr  = LineReader (ll)
			msg = Message (lr)
			
			xref = msg.getheader ("xref")
			xxr = xref.split(' ')
			server = xxr[0]
			pgroups = map (lambda x: x.split(':'),xxr[1:])
			#~ print '** pgroups', pgroups
			msgnum = int(msgnum[:-4])
			group_name = ''
			for x, y in pgroups:
				#print 88, x, y
				if int(y) == msgnum:
					group_name = x 
					break
			MM = '%s/%s' % (dn, msgnum)
			f1 = dumptextfile(MM+'.{M}')
			f2 = ll      #dumptextfile(MM+'.{C}')
			
			return server, group, msgnum, f1, f2
		finally:
			del lr, msg

def main(args):
	if len(args)>1:
		dn = args[1]
	else:
		dn = 'xx'
	gn2o    = GetNews2Onet()
	listing = os.listdir (dn)
	cur     = 0
	last    = len (listing)
	first   = 0
	measure = OpMeasure(first,last,last,cur)
	for each in listing:
		cur = cur + 1
		#print '== Trying %s/%s (%d of %d) [%s]' % (dn, each, cur, last, \
		#	time.ctime(time.time()))
		measure.startOp(cur)
		gn2o.do_file(dn, each)
		measure.endOp()

def prof(args):
	import profile
	profile.run('main(args)', 'fooprof')
	import pstats
	p = pstats.Stats('fooprof')
	p.sort_stats('time').print_stats() #10)

#prof (sys.argv)
main (sys.argv)

#
# eof
#
