import os
import sys
import time

from AppWorks.Invocation.OnetAddNewsgroupMessage import OANM1_JOB_EXECUTOR, Onet_EmptyMessage
from etoffiutils import dumptextfile, true, false
from netapps.GetNews2Onet.MailExtractors import MailExtractEML, MailExtractCBracket, MailExtractNull, WrongFormat, \
	MexErrorEmpty


class MailExtractMultiplexer:
	def __init__(self):
		self.executor = OANM1_JOB_EXECUTOR(None)
		self._eml = MailExtractEML(self.executor)
		self._cbr = MailExtractCBracket(self.executor)
		self._nul = MailExtractNull(self.executor)
	
	def get(self, filename):
		extension = filename[-4:].lower()
		if extension == '.eml':
			return self._eml
		elif extension == '.{c}':
			return self._cbr
		else:
			return self._nul


class GetNews2Onet:
	def __init__(self):
		self.multiplexer = MailExtractMultiplexer()
	
	def do_file(self, dirname, filename):
		fullname = '%s/%s' % (dirname, filename)
		try:
			ll = dumptextfile(fullname, true)
			don = self.translate_message(ll, dirname, filename)
			if don != false:
				os.unlink(fullname)
		except WrongFormat, e:
			print '** wrong format'
		except Onet_EmptyMessage, e:
			#			print e
			print '** Message is empty'
		except IOError, e:
			print '== Error Decoding', filename
			print '\t', e
			print '================='
	
	def translate_message(self, ll, dn, filename):
		extractor = self.multiplexer.get(filename)
		if isinstance(extractor, MailExtractNull):
			return false
		
		res = extractor.extract_srv_info(ll, dn, filename)
		if res is None:
			return
		if isinstance(res, MexErrorEmpty):
			print >>sys.stderr, "Message is empty "+res.field
			return
		server, group, msgnum, f1, f2 = res
		
		# generate spectionary
		spectionary = {}
		spectionary['server'] = server
		spectionary['group_name'] = group
		spectionary['msgnum'] = msgnum
		spectionary['options'] = 'save-headers extract-contents-in-shared delete-orig'
		
		# invoke message adding component
		extractor.add_newsgroup_message(time.ctime(time.time()), spectionary, f1, f2)
