import os
import string
import time

true = 1
false = 0

### etoffi UTILS ###

def quickReadFunc(filename, fn, strip=false, stripcomments=false):
	return map (fn, dumplines(open(filename).readlines(), strip, stripcomments))

def dumptextfile(filename, strip=false, stripcomments=false):
	return dumplines(open(filename).readlines(), strip, stripcomments)

def dumplines(l, strip=false, stripcomments=false):
	if strip:
		l = map(lambda e: e.rstrip(), l)
	if stripcomments:
		l = map(lambda e: strip_comments(e), l)
	
	return l

def strip_comments(line):
	r = string.find(line, '#')
	if r == -1:
		return line
	if r == 0:
		return ''
	if line[r-1:][0] == '\\':
		return strip_comments(line[r+1:])
	raise line[r:]

### etoffi UTILS ###

def nequals(s1, s2):
	return s1[:len(s2)] == s2


def ensure_directory_present(dn, logfile=None):
	try:
		os.makedirs(dn)
	except OSError, e:
		if e.errno != 17: # EEXIST
			if logfile:
				logfile.write(e)

def quickWrite(fn, lines, addNL=true):
	"""fn:FileName lines:List<?a> addNL:bool=true"""
	f = open(fn, 'w')
	if addNL:
		f.writelines(map(lambda e: "%s\012" % str(e), lines))
	else:
		f.writelines(lines)
	f.close()

def inc_until_nofile(num, pre, post, logfile=None):
	try:
		qr = '%s%d%s' % (pre, num, post)
		while os.stat(qr):
			num = num + 1
			qr = '%s%d%s' % (pre, num, post)
	except OSError, e:
		if e.errno != 2:
			if logfile:
				logfile.write(e)
	return num	

def inc_until_nofile_fn(num, fun, logfile=None):
	try:
		qr = apply(fun, (num,))
		while os.stat(qr):
			num = num + 1
			qr = apply(fun, (num,))
	except OSError, e:
		if e.errno != 2:
			if logfile:
				logfile.write(e)
	return num	

def Fill(num, fillspec='0', length=3):
	""" does not truncate data. then full number num will be output. 
	    fillspec must be a char 
	"""
	ret = str(num)
	l   = length - len(ret)
	if l > 0:
		ret = '%s%s' % (fillspec * l,ret)

	return ret

def combine_lists(l1, l2):
	r = []
	for each in l1:
		r.append(each)
	for each in l2:
		r.append(each)
	return r
	
def add_to_head(ii, ll):
	""" item, thelist -> (a new) List """
	r = [ii]
	return combine_lists(r, ll)
	

def OIX_File_Attr_QuickPut(filename, attrname, attrval):
	f = open('attr.dat', 'ab+')
	if f:
		f.write('--\n%s\n%s:\t%s\n' % (filename, attrname, attrval))
		f.close()
		
def join_dict(dict):
	r = ''
	for each in dict.items():
		r = "%s%s: %s\012" % (r, each[0], each[1])
	return r
	
def progressiveParse(Str, Sep):
	""" Jan-05 """
	r=string.split(Str, Sep)
	rv=[]
	for each in xrange(len(r), 0, -1):
		m=string.join(r[:each], '/')+'/'
##		print m
		rv.append(m)
	return rv #.reverse()

def reverse_findfile(fn):
	""" Jan-05 """
	l=progressiveParse(fn, '/')
	for each in l:
		if os.stat(each):
			return each

def ____cvg(x):
	if x.errno!=2:
		print x
def read_firstline_from_file(filename, strip=true, eh=____cvg):
	""" Jan-06 (1734) """
	rv=None
	try:
		F  = open(filename)
		rv = F.readline()
		if strip:
			rv = rv[:-1]
		F.close()
	except IOError, e:
		if eh: eh(e)
	return rv

def quickAppend(fn, lines, addNL=true):
	""" fn:FileName lines:List<?a> addNL:bool=true 01-Jan-13 (0349) """
	f = open(fn, 'ab+')
	if addNL:
		f.writelines(map(lambda e: "%s\012" % str(e), lines))
	else:
		f.writelines(lines)
	f.close()

#--
from base64 import encodestring as b64_encode_

def b64_encode(s):
	return b64_encode_(s)[:-1]
#--	
from quopri import encodestring as encode_quopri_
def qpi_encode(s):
	return encode_quopri_(s)
#--	
____badchr = ' <>"{}#|\\^~[]`@:\033?%' + "'"
def encchr(ch):
	def _makret(ch):
		return '%%%2x' % ord(ch)
	for each in ____badchr:
		if each == ch:
			return _makret(each)
	return ch
def oixfs_encode(oldname):
	rv=''
	for each in oldname:
		rv += encchr(each)
	return rv
____x2badchr = '<>%&' #+'\r\n'
def x2encchr(ch):
	def _makret(ch):
		return '%%%2x' % ord(ch)
	for each in ____x2badchr:
		if each == ch:
			return _makret(each)
	return ch
def x2_encode(oldname):
	rv=''
	l = 0
	for each in oldname:
		mm = x2encchr(each)
		l = l + len(mm)
		if l > 64:
			l = 0
			rv += '\n'
		rv += mm
	return rv
def x2_decode (instr):
	outstr = ''
	for each in instr:
		pass
	return outstr
def xstat(fn):
	import os
	try:
		os.stat(fn)
#		print 'XSTAT /+/ ' + fn
		return true
	except OSError:
		print 'XSTAT \\-\\ ' + fn
		return false
def string_right(str, len):
	return str[-len:]
def string_upto(str, spot):
	return str[:-spot]
def checkRemoveEnd(instr, endwith):
	le = len(endwith)
	if string_right(instr,le)==endwith:
		rv=string_upto(instr, le)
	else:		
		rv=instr
	return rv


# from rfc822.py. thanks Python!!
def formatdate(timeval=None):
	"""Returns time format preferred for Internet standards.

	Sun, 06 Nov 1994 08:49:37 GMT  ; RFC 822, updated by RFC 1123
	"""
	if timeval is None:
		timeval	= time.time()
	return "%s"	% time.strftime('%a, %d	%b %Y %H:%M:%S GMT',
								time.gmtime(timeval))

#eof
