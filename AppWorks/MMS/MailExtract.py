import sys, os, string, mimetools, multifile
from etoffiutils import oixfs_encode, false, true, nequals, quickAppend
from etoffiutils2.foo import octal_str_to_decimal
from etoffiutils2.LineReader import LineReaderN

'''Version History:
1.0		20 Jul 2000	Initial	release.
1.0.1	22 Jul 2000	Added --help option.
2.7		11 Mar 2001 Cleaned code a liitle and created MailExtract class
2.7.1   15 Jul 2002 refactorings: octal_str_to_decimal, UU#decode, LineReaderN
2.7.5   15 Jul 2002 refactorings: out_file_str_to_fp
'''

VERSION	= '2.7.5'

class MailExtractError: pass
error =	MailExtractError

def fix_file_name(fn):
	"""	fix_file_name(String)->String
		--
		remove illegal chars. according to oixfs_encode
	"""
	ofn = fn
	fn = oixfs_encode(fn)
	if ofn != fn:
		men.fix_file_name (ofn, fn)
	return fn

class OutFile:
	def __init__(self, fn=None):
		if fn: self.F = self.open(fn)
	def open(self, filename, mode='wb', buffering=8192):
		ffn = os.path.dirname (filename) + '/' + fix_file_name (os.path.basename (filename))
		if ffn != filename: 
			#~ print '711\a'
			quickAppend('diffname',[filename,ffn,'--'])
		self.F = open(ffn, mode, buffering)
		self.name = filename
		return self.F
	def write(self, v):
		return self.F.write(v)
	def close(self):
		return self.F.close()
class InFile:
	def __init__(self, fn=None):
		if fn: self.F = self.open(fn)
	def open(self, filename, mode='rb', buffering=8192):
		self.F = open(filename, mode, buffering)
		self.name = filename
		return self.F
	def readline(self):
		return self.F.readline()
	def close(self):
		return self.F.close()
def nErr(xx):
	sys.stderr.write(xx+'\n')
def nOut(xx):
	sys.stdout.write(xx+"\n")

class MailExtractNotifier:
	##
	def emit_err_string (self, xx):
		sys.stderr.write(xx+'\n')
	def emit_string (self, xx):
		#sys.stderr.write(xx+'\n')
		pass
	##
	def uudecode_set_file_name (self, fn):
##		self.emit_string ("UU: [output_file_name] %s" % fn)
		pass
	def uudecode_warning (self, the_text):
		self.emit_err_string ("UU: [Warning] %s" % the_text)
	def decode_mime (self, partno, kkp, name):
		self.emit_string ("MIMEDecode: [saving_part_%d%s] -> (%s)" % (partno, kkp, name))
	def fix_file_name (self, ofn, fn):
		self.emit_string ("fix_file_name %s" % fn)

men = MailExtractNotifier ()

class UUError(Exception):
	pass
class UUBeginLineError(UUError):
	pass
class UU:
	
	def	__init__(self, dirname=None, xx=None):
		self.dirname = dirname
		self.xx = xx

	def GetOutFile(self, filename):
		return self.xx.GetOutFile(filename)
	def GetInFile(self, filename):
		return self.xx.GetInFile(filename)
		
	def	decode(self, in_file, out_file=None, mode=None):
		""" Decode uuencoded file
		    #decode (in_, out_, mode) -> Void
		    -- 
		    will open in and out and decode in to out, setting mode
		"""
		#
		# Open the input file, if needed.
		#
		if in_file == '-':
			in_file = sys.stdin
		elif type(in_file) == type(''):
			in_file = self.GetInFile(in_file)
		#
		# Read until a begin is	encountered	or we've exhausted the file
		#
		while 1:
			hdr	= in_file.readline()
			if not hdr:
				raise UUBeginLineError, 'No valid begin line found in input file'
			if nequals(hdr,'begin'):
				hdrfields =	string.split(hdr)
				assert hdrfields[0] == 'begin'
				if len(hdrfields) == 1:
					# false positive
					return 
				else:
					if len(hdrfields) == 3 or hdrfields[1]=='644':
						try:
							string.atoi(hdrfields[1], 8)
							break
						except ValueError:
							pass
			
		if out_file	== None:
			out_file = string.join(hdrfields[2:])
		if mode	== None:
			mode = octal_str_to_decimal(hdrfields[1])
		#
		# Open the output file
		#
		if out_file	== '-':
			out_file = sys.stdout
		elif type(out_file) == type(''):
			out_file = self.xx.out_file_str_to_fp(self, out_file, fix_file_name, men, mode)
		#
		# Main decoding	loop
		#
		import binascii

		s =	in_file.readline()
		while s and s != 'end\n':
			try:
				data = binascii.a2b_uu(s)
			except binascii.Error, v:
				# Workaround for broken	uuencoders by /Fredrik Lundh/
				nbytes = (((ord(s[0])-32) & 63)	* 4	+ 5) / 3
				try:
					data = binascii.a2b_uu(s[:nbytes])
					men.uudecode_warning (`v`)
				except binascii.Error, e:
					nErr (`e`)
					nErr (data)
			out_file.write(data)
			s =	in_file.readline()
		if not str:
			raise Error, 'Truncated input file'
#	def out_file_str_to_fp(self, out_file_name):
#		return self.xx.out_file_str_to_fp(self, out_file_name)

#~ class mxUU(UU):
	#~ def GetOutFile(self, filename):
		#~ return OutFile(filename)
	#~ def GetInFile(self, filename):
		#~ return InFile(filename)
	
def	usage():
	cmd	= os.path.basename(sys.argv[0])
	sys.stderr.write("Usage: %s	[-u] [--help] file1 [... filen] [-d destdir]\n" % cmd)

	
class MailExtract:
	def GetOutFile(self, filename):
		return OutFile(filename)
	def GetInFile(self, filename):
		return InFile(filename)
	def set_outdir (self, outdir):
		self.outdir = outdir
	def	do_uu(self, src):
		''' decode a uuencoded file '''
#		nOut ("MailExtract: [uudecode] %s" % `src.fp`)
		try:
			uu = UU(self.outdir, self)
##			uu.GetOutFile = self.GetOutFile
##			uu.GetInFile = self.GetInFile
			uu.decode(src.fp)
		except UUBeginLineError, e:
			nErr ("UUDecode: [Error] Not a UUEncoded file (%s)" % src.fp.name)
		except UUError, e:
			print '** TODO: elimnate errors l148'
			nErr ("UUDecode: [error] %s" % e)
	def	do_mime(self, src, dstfile):
		""" src: multifile.MultiFile, 
			Read mail message from src multifile object and write
			attached files to self.outdir
		"""
		headers	= mimetools.Message(src, src.seekable)
		if headers.getmaintype() !=	"multipart":
#			raise error, "message is not multipart	MIME"			
			return 0
		boundary = headers.getparam("boundary")
		if not boundary:
			raise error, "message boundary not specified"
		partno = 0
		src.push(boundary)
		src.read()			# Read to first	boundary.
		while not src.last:
			src.next()
			headers	= mimetools.Message(src, src.seekable)
			partno = partno	+ 1
			name = headers.getparam("name")
			if self.namedonly and not name:
				src.read()	# Read to next boundary.
				continue
			encoding = headers.getencoding()
			if not encoding:
				raise error, "unknown message encoding"
			if self.outdir:
				if not name: name = "part_%d" % (partno,)
				dstfile	= self.GetOutFile(os.path.join(self.outdir,name))
			else:
				name = os.path.basename(dstfile.name)
			if encoding != 'base64':
				kkp = ' (%s encoding)' % encoding
			else:
				kkp = ''
			men.decode_mime (partno, kkp, name)
			if encoding	== "7bit":
				mimetools.copyliteral(src, dstfile)
			else:
				mimetools.decode(src, dstfile, encoding)
			if self.outdir:
				dstfile.close()
		return 1
	def	mailextract(self, src, dstfile):
		if self.do_mime(src, dstfile) == 0:
			self.do_uu(src)
	def	do_decode(self, source_file):
		try:
			if type(source_file) == type('') and os.path.isdir (source_file):
				nOut ("MailExtract: [do_decode] cannot `extract' a directory (%s)" % source_file)
				return
			source = self.GetInFile(source_file)
			self.do_decode_lines (self, source, 1)
		except IOError, e:
			print 'TODO: elimnate errors l217'
			print e
			
	def do_decode_lines(self, source, k=0):
			self.namedonly = false # TODO: fix this
			if k == 0:
				source = LineReaderN(source)
			mf = multifile.MultiFile(source, 0)
			# extract file to stdout
			if not self.outdir:
				# extract file to stdout
				self.mailextract(mf, sys.stdout)
			else:
				if os.path.isdir(self.outdir):
					# extract file to a directory
					self.mailextract(mf, None)
				else:
					# extract file into another file
					# TODO: use BackupFile here
					dstdir, dstfile = os.path.split(self.outdir)
					if dstdir and not os.path.isdir(dstdir):
						raise error,"path %s not found" % dstdir
					f =	self.GetOutFile(self.outdir)
					self.mailextract(mf, f)
					f.close()
			source.close()
	
	def out_file_str_to_fp(self, xx, out_file_name, fix_file_name, men, mode):
		if xx.dirname:
			out_file_name = "%s/%s" % (xx.dirname, fix_file_name( out_file_name))
		men.uudecode_set_file_name (out_file_name)
		fp = self.GetOutFile(out_file_name)
		try:
			os.chmod(out_file_name, mode)
		except OSError:
			pass
		return fp

#
# eof
#
