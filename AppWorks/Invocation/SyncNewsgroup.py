from GetNews_.NNGET import *
from AppWorks.Util.AwxDBi import AwxDBi
from AppWorks.Jobs import Job
from etoffiutils import dumptextfile
import time

nn = NNGET()
nn.setopts(None, 1)

def get_group_info (server, group_name):
	user_name, passwd = get_group_login_info (server, group_name)
#	nn = NNGET()
	global nn
	ss = nn.obtain (server, 119, user_name, passwd)
	if not ss:
		res, ft, ls, user_name, passwd = 0, 0, 0, None, None
	else:
		S = nn.select(ss, group_name)
		(ft, ls) = S.first, S.last
#		nm, rs, mc, ft, ls = nn.query(ss)
		res = 1
	return res, ft, ls, user_name, passwd
	
def get_group_login_info (server, group_name):
	""" (server, group_name) -> user_name, passwd """
	user_name = None
	passwd    = None

	v = AwxDBi()
	s = v.enum('~/MailSystem/News/Sources', AwxDBi.EnumFlat)

	for each in s:
		mm = '~/MailSystem/News/Sources/%s' % each.getName()
		xx = '%s/name' % mm
		kk = v.getStr(xx)
		if kk == server:
			user_name = v.getStrWithDefault('%s/login' % mm, 'bad_user_name$$')
			passwd    = v.getStrWithDefault('%s/pass'  % mm, '$$$bad_password')
			print user_name, passwd
	return user_name, passwd
	
def nnget (server, group_name, user, passwd, curmsg):
	print '/%s/%s/%d' % (server, group_name, curmsg), 
#	print (server, group_name, user, passwd, curmsg)
	if user:
		print '\t-> ', (user, passwd)
	else:
		print ''
#	nn = NNGET()
	global nn
	ss = nn.obtain (server, 119, user, passwd)
	if ss:
		nn.select(ss, group_name)
		lines, attr = nn.retrieve (ss, curmsg)
		if lines == None:
			print attr['NNTP-Error']
	else:
		lines, attr = None, None

	return lines, attr

def print_spec_list(sl):
	for each in sl.keys():
		print each + '\t\t' + sl[each]

def do_job(j, jm):
	print 'SyncNewsgroup ================================================================='

	print_spec_list (j.spec_list)
	
	group_name = j.spec_list['group_name']
	server     = j.spec_list['server']
#	async      = j.spec_list['async']
	interval   = j.spec_list['interval']

	time.sleep (int(interval))
	
	the_id     = 'sync_newsgroup-%s-%s' % (group_name, `time.time()`)
	specl      = {}
	
	if 1:   # common speclist attributes
			specl['invokable-class'] = 'SyncNewsgroup'
#			specl['async']      = async
			specl['group_name'] = group_name
			specl['server']     = server
			specl['interval']   = interval
			specl['sync_type']  = 'update'

			if j.spec_list.has_key('post-invokable'):
				specl['post-invokable'] = j.spec_list['post-invokable']
			if j.spec_list.has_key('post-invoke-options'):
				specl['post-invoke-options'] = j.spec_list['post-invoke-options']

	if j.spec_list['sync_type'] == 'update':
		user, passwd = get_group_login_info (server, group_name)

		curmsg = int(j.spec_list['minnum'])
		
		lines, attr = nnget (server, group_name, user, passwd, curmsg)
##		lines = dumptextfile('29272.eml', strip=1)
		attr = {}
		
		if curmsg <= int(j.spec_list['maxnum']):
			specl['minnum']     = `curmsg+1`
			specl['maxnum']     = j.spec_list['maxnum']
			
			jj = Job.Job(the_id, len(specl.keys()), specl, 'invocation', [])
			jm.insert (jj)

			try_post_invoke (j, jm, (lines, attr))

	elif j.spec_list['sync_type'] == 'start':
		res, st, fin, user, paswd = get_group_info (server, group_name)
##		res, st, fin, user, paswd = 1, 29272, 29667, None, None
		
		if res == 1:
			specl['minnum']     = `st`
			specl['maxnum']     = `fin`		
		
			jj = Job.Job(the_id, len(specl.keys()), specl, 'invocation', [])
			jm.insert (jj)

def try_post_invoke (j, jm, pre_res):
##	print ("{")
##	print_spec_list (j.spec_list)
##	print ("}")
#	print pre_res
	if j.spec_list.has_key('post-invokable'):

		ss = j.spec_list['post-invokable']

		print ss	

		# <begin_whoa>
		mm = __import__('AppWorks.Invocation.'+ss)
		kl = mm.__dict__['Invocation'].__dict__[ss]
		#print kl
		# </end_whoa>

		specl = {}
		if j.spec_list.has_key('post-invoke-options'):
			specl['options'] = j.spec_list['post-invoke-options']
		else:
			specl['options'] = ''
		specl['server'] = j.spec_list['server']
		specl['group_name'] = j.spec_list['group_name']
		specl['msgnum'] = j.spec_list['minnum']
		specl['server'] = j.spec_list['server']
#		specl['process_type'] = 'pre_res'
#		specl['pre_res'] = pre_res # make sure this holds the result of the previous operation
		job = Job.Job ((j.id+'post-invokable-'+ss)[:100]+`time.time()`, len(specl.keys()), specl, 'post-invocation', pre_res)
		if kl:
			return kl.do_job(job, jm)
	
