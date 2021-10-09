import os
import string
import time

from AppWorks.MMS.MailExtract import MailExtract
from AppWorks.Net.Onet import OnetObj
from etoffiutils import quickWrite, b64_encode, qpi_encode, ensure_directory_present, true, false
from etoffiutils2.text import getQuoted

#
# OnetAddNewsgroupMessage.py
# --------------------------
#
# j.spec_list ->
# 	server, group_name, msgnum, options
# j.spec_list['options'] ->
#	store-in-filesystem
#		mangle-server-name
#		mangle-group-name
#	save-headers
#	extract-contents
#	extract-contents-in-shared
#	delete-orig
# j.params ->
#	(msg_lines, oixfs_attr_dict)
#		|           +-> written as onet props
#		+---> obvious
#

mangle_name = b64_encode

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
class Onet_EmptyMessage (Exception):
	pass

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
def identity(x): return x
def choose(x,y,z): 
	if x: 
		return y
	return z

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
def ensure_clear_name(filename):
	if os.path.isfile (filename):
		newfn = filename
		i = 1
		while os.path.isfile (newfn):
			newfn = '%s.~%d~' % (newfn, i)
			i = i + 1
		os.rename(filename, newfn)
		assert os.path.isfile (newfn)
		assert not os.path.isfile (filename)

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
def cgi_escape (s, quote=None):
    """Replace special characters '&', '<' and '>' by SGML entities."""
    s = string.replace(s, "&", "&amp;") # Must be done first!
    s = string.replace(s, "<", "&lt;")
    s = string.replace(s, ">", "&gt;",)
    if quote:
        s = string.replace(s, '"', "&quot;")
    return s

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
def extract_headers_from_message (msg):
	if type(msg) == type(''):
		print 'oops'
	r = []
	for each in msg:
#		print each
		if each == '':
			break
		r.append (each)
	return r

def extract_info_from_msg (headers):
	h = {}
	for each in headers:
		try:
			p = each.index (':')
			h[each[:p].lower()]=each[p+1:]
#			print each[:p], each[p+1:]
		except ValueError:
			pass

	try:
		aa = h['from'].lstrip()
	except KeyError:
		raise Onet_EmptyMessage ()
	author, author_email = '', ''
	if aa[0] in ('\"', "'"):
		author, author_email = getQuoted(aa)
	else:
		aa = aa.split()
		if len(aa) == 2:
			author, author_email = aa[0], aa[1]
		else:
			author, author_email = aa[0][:aa[0].find('@')], aa[0]
	msgid, date = (h['message-id'], h['date'])
	try:
		posting_host = h['nntp-posting-host']
	except KeyError:
		posting_host = ''
	
	return  author, author_email, msgid, date, posting_host 

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
def today_date():
	r = time.strftime('%Y-%b-%d (%H%M)', time.localtime(time.time()))
	return r

#
# dummy
#
#

class OANM1_JOB_EXECUTOR:
	def __init__(self, jm):
		self.msg_st_root = ''
		self.onet_base   = ''
		
		self.read_cfg_file()
	
	def read_cfg_file(self):
		try:
			# using strip instead of [:-1] fixes by-dirname-...^M bug
			f = open ('OnetAddNewsgroupMessage.rc')
			f.readline()
			l1 = f.readline().rstrip()
			f.readline()
			l2 = f.readline().rstrip()
			f.close()
		except :
			l1, l2 = 'c:/_', 'e:/_onet/by-%s'
		try:
			f = open ('OnetAddNewsgroupMessage.rc', 'w')
			f.write ('# message_store_root: ~/local/data/GetNewsX/\n')
			f.write ('%s\n# oname_base: ~onet-storage/by-%%s\n%s\n' % (l1, l2))
			f.close()
		except:
			print 'error writing config'
		self.msg_st_root = l1
		self.onet_base   = l2
	##	print 'msg_st_root', msg_st_root
	##	print 'onet_base', onet_base
	
	def get_news_msg_st_root (self):
		return self.msg_st_root
	def get_onet_base (self, x):
		return self.onet_base % x
	def res_id_to_path (self, x):
		return x #.replace ('-','/')
	
	def execute(self, j):
		print 'OnetAddNewsgroupMessage ======================================================='
		print '== JOBID -->>', j.id, j.job_type
		
		#	print j.job_type
		#	print_spec_list (j.spec_list)
		
		msg_lines = j.params[0]
		oix_attrs = j.params[1]
		
		if msg_lines is None:
			log("719: skip null message")
			return
			
		server = j.spec_list['server']
		msgnum = j.spec_list['msgnum']
		grpnam = j.spec_list['group_name']
		l      = j.spec_list['options'].split()
	
	##	print oix_attrs
	
		delete_orig = 0
		extract_contents = 0
		
		for each in l:
			
			if "delete-orig" == each:
				delete_orig = 1
			if "extract-contents" == each:
				extract_contents = 1
			if "extract-contents-in-shared" == each:
				extract_contents = 2
			if "store-in-filesystem" == each:
				
				y = choose("mangle-server-name" in l, mangle_name, identity)
				z = choose("mangle-group-name"  in l, mangle_name, identity)
				
				dl = '%s/%s/%s/' % (self.get_news_msg_st_root(), y(server), z(grpnam))
				ensure_directory_present (dl)
				sl = dl + msgnum
				quickWrite (sl, msg_lines, true)
				
				if "save-headers" in l:
					quickWrite (sl+".headers", extract_headers_from_message (msg_lines), true)
	
		base  = self.get_onet_base ('basic-resource-id')
		resid = '[%s][%s][%s]' % (server, grpnam, msgnum)
		fnX   = '%s/OnetAddNewsgroupMessage2/%s/%s' % (base, server, grpnam)
		fn_   = '%s/%s' % (fnX, msgnum)
		ensure_directory_present (fnX+'/_onet')
		ensure_directory_present (fnX+'/_shared')
		fn     = '%s/%s' % (fn_, msgnum)
	
		# -------------------
		#  start writing xml
		# -------------------
	
		if not delete_orig:
			if msg_lines is not None:
				quickWrite (fn, msg_lines, true)
	
		dpyname = '%s in %s at %s' % (msgnum, grpnam, server)
		headers = extract_headers_from_message (msg_lines)
		author, author_email, msgid, date, posting_host = extract_info_from_msg (headers)
		keywords = ''
		modelist = ''
		storage_location = msgnum+'.msg'
		if "save-headers" not in l:
			headers = None
	
		onet_obj=OnetObj()
		onet_obj.set_dpy_name(dpyname)
		for n,v in oix_attrs:
			onet_obj.set_prop(n,v)
		out = """<?xml version="1.0"?>
<onet_file version="2" brid="%s">
	<type simple-mime="image/jpeg" complex-mime="image/jpeg" />
	<versions>
		<version id="v1.0" displayname="%s">
			<author name="%s" email="%s" ipaddy="%s" />
			<submittor logon="OnetAddNewsgroupMessage2" ipaddy="127.0.0.1" date="%s" />
			<storage location="%s" />
		</version>
	</versions>
	<permissions order="allow, deny">
		<grant name="class:modify" to="user:GetNews" />
		<grant name="class:view" to="user:*" />
	</permissions>
	<keywords>
		%s
	</keywords>
	<modelist>
		%s
	</modelist>
	<properties>
	<property name="datetime" simple-type="string" complex-type="time/internet">
		%s
	</property>
	<property name="Message-ID" simple-type="string" complex-type="rfc822/message-id">
		%s
	</property>	
	"""	% 	(resid, dpyname, author, author_email, posting_host, today_date(), 
					storage_location, keywords, modelist, date, cgi_escape (msgid)
				)
		if headers != None:
			out += """		<property name="rfc822-header" author="user:GetNews" type="long_string" encoding="quoted-printable/cgi_escape">"""
			out += qpi_encode(string.join (map(lambda x: cgi_escape(x), headers), '\n'))
			out += """		</property>""" 
		out += """</properties>\n</file>\n"""
	
		if extract_contents != 2:
			quickWrite (fn+".onet", [out], false)
		
		# --------------------
		#  finish writing xml
		# --------------------
	
		if extract_contents == 1:
			ensure_directory_present (fn_)
			me2 = MailExtract()
			me2.set_outdir (fn_)
			me2.do_decode_lines (msg_lines)
		elif extract_contents == 2:
		
			class MailExtract_Special (MailExtract):
				def out_file_str_to_fp(self, _1, out_file_name, fix_file_name, men, mode):
					assert type(out_file_name)==type('')
					filename = fix_file_name( out_file_name)
					X = "%s/_shared/(%d)-%s" % (self.outdir, self.cur_msg_num, filename)
					#~ print 67122, 'hfdsafbjdlfnfa', X
					men.uudecode_set_file_name (X)
					fp = self.GetOutFile(X)
					assert not os.path.isfile(X)
					try:
						os.chmod(X, mode)
					except OSError, e:
						print 9887, e.__class__.__name__, e
					return fp
				def GetOutFile (self, filename):
					filename = filename.replace ('\\', '/')
					ensure_clear_name(filename)
					return MailExtract.GetOutFile (self, filename)
	
			quickWrite (fnX+"/_onet/"+msgnum+".onet", [out], false)
			
			me2 = MailExtract_Special()
			me2.set_outdir (fnX)
			me2.cur_msg_num = int(msgnum)
			me2.do_decode_lines (msg_lines)

def do_job(j, jm):
	OANM1_JOB_EXECUTOR(jm).execute(j)

#eof
