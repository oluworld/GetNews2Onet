#!/usr/bin/env python
import string
import os
from etoffiutils import *
from AppWorks.Services.RCDBiHandler import SplitLine, getQuoted
from Job import Job
from BufferedFileReader import FileReader, Foo

finished_reading = 0
global_jm = None

class JobManager:
	def __init__ (self, xif):
		self.input_file = xif
		self.msg_q      = []
		if xif == 1:
			finished_reading = 1
	def get_next (self):
#		self.msg_q.append()
		if self.msg_q == []:
			return self.read_job(self.input_file)
		else:
			r = self.msg_q[0]
			self.msg_q = self.msg_q[1:]
			return r
	def insert (self, job):
		self.msg_q.append (job)		
			
	def read_job(self, jfi):
		if finished_reading == 1:
			return None
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
				specl[n]=v
			k = []
			l = jfi.readline()[:-1]
			while l != '%%':
				k.append( l )
				l = jfi.readline()[:-1]
		except Foo, e:
			global finished_reading
			finished_reading = 1
#			print 'exception 0', e
#			print "finished_readling = 1, id =", id 		
		global finished_reading
		if finished_reading == 1:
			rv = None
		else:
			rv = Job(id, nspec, specl, type, k)
		return rv

def do_job(job):
#	print 'job_type='+job.job_type
	if job.job_type == 'shell':
		fn = "JM-%d" % inc_until_nofile(1, "JM-", '')
		quickWrite(fn, job.params)
		rv = os.system('sh %s' % fn)
		rv2 = os.system('rm %s' % fn)
		if not rv or not rv2:
			return 0
		return 1
	if job.job_type == 'invocation':
		ss = job.spec_list['invokable-class']
#		for eachx in job.spec_list.keys():
#			print m, eachx, "\t", job.spec_list[eachx]
#			m = m+1
##		if not job.spec_list.has_key('invokable-class'):
##			print "oops"
		# <begin_whoa>
		mm = __import__('AppWorks.Invocation.'+ss)
#		print dir(mm.__dict__['Invocation'].__dict__[ss])
		kl = mm.__dict__['Invocation'].__dict__[ss]
		# </end_whoa>
		if kl:
			return kl.do_job(job, global_jm)

	return 0

def spec_list_to_list(sl):
	r = []
	for each in sl.keys():
		r.append (each + ' ' + sl[each])
	return r
	
def write_job(job, jfo):
	s = [ '%%', job.id, str(job.job_type), str(job.nspec) ]
	s2 = combine_lists(spec_list_to_list(job.spec_list), job.params)
	s = combine_lists(s, s2)

#	print 's=',s
	
	jfo.writelines(map(lambda e: "%s\012" % str(e), s))

def main():
#	jfi = open('jobs.dat', 'r')
	jfo = open('jobs-done.dat', 'a+')

	jfi = FileReader()
	jfi.open('jobs.dat')
	global global_jm
	global_jm = JobManager(jfi)
	jm = global_jm 
	
	try:
		deferred_jobs = []

		try:
			while 1:
				job = jm.get_next()
#				job = read_job(jfi)

				if job:
					if do_job(job):
						write_job(job, jfo)
					else:
						deferred_jobs.append(job)
				else:
					break
		except KeyboardInterrupt: #Exception, e:
			print 'exception 1', e
		jfo.close()

		jfo = open('jobs.dat.o', 'w')
		for each in deferred_jobs:
			write_job(each, jfo)
		jfo.write('%%\012')
		jfo.writelines(jfi.readlines())
	except KeyboardInterrupt: #Exception, e:
		print 'exception 2', e
	jfi.close()
	jfo.close()

#	os.system('sh -c "rm -f jobs.dat && mv jobs.dat.o jobs.dat"')

if __name__ == '__main__':
	main()
