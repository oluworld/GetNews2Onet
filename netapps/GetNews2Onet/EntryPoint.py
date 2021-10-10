import os

from etoffiutils2.OpMeasure import OpMeasure
from netapps.GetNews2Onet.GetNews2Onet import GetNews2Onet


def logic(args):
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


def prof(args, filename):
	import profile
	# profile.run('import netapps;netapps.GetNews2Onet.EntryPoint.logic(args)', filename)
	prof = profile.Profile()
	prof.runcall(logic, (args,))
	prof.dump_stats(filename)
	import pstats
	p = pstats.Stats(filename)
	p.sort_stats('time').print_stats()  # 10)


def main(args):
	import argparse
	parser = argparse.ArgumentParser(description='Convert GetNews to Onet.')
	
	parser.add_argument('-p', nargs=1, type=str, help="Profile the application into <filename>")
	
	a = parser.parse_args(args[1:])
	
	profile_it = a.p
	if profile_it is not None:
		prof(args, profile_it[0])
	else:
		logic(args)
