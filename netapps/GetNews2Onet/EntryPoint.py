import os

from etoffiutils2.OpMeasure import OpMeasure
from netapps.GetNews2Onet.GetNews2Onet import GetNews2Onet


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
