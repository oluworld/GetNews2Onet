import os, sys, time
from etoffiutils import dumptextfile, true
from AppWorks.Invocation.OnetAddNewsgroupMessage import Onet_EmptyMessage, OANM1_JOB_EXECUTOR
from etoffiutils2.OpMeasure import OpMeasure
from netapps.GetNews2Onet.MailExtractors import MailExtractNull, MailExtractEML, MailExtractCBracket, WrongFormat


class pException(Exception): pass


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
			self.translate_message(ll, dirname, filename)
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
		res = extractor.extract_srv_info(ll, dn, filename)
		if res is None:
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


#class NullMessage(Exception):
#	pass


def main(args):
	if len(args) > 1:
		dn = args[1]
	else:
		dn = 'xx'
	gn2o = GetNews2Onet()
	listing = os.listdir(dn)
	cur = 0
	last = len(listing)
	first = 0
	measure = OpMeasure(first, last, last, cur)
	for each in listing:
		cur = cur + 1
		# print '== Trying %s/%s (%d of %d) [%s]' % (dn, each, cur, last, \
		#	time.ctime(time.time()))
		measure.startOp(cur)
		gn2o.do_file(dn, each)
		measure.endOp()


def prof(args):
	import profile
	profile.run('main(args)', 'fooprof')
	import pstats
	p = pstats.Stats('fooprof')
	p.sort_stats('time').print_stats()  # 10)


# prof (sys.argv)
main(sys.argv)

#
# eof
#
