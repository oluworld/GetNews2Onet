#
#
#


class OnetObj:
	
	def __init__(self):
		self.V = {}
		self.saved_properties = ''

	def add_version(self, version_id, dpyname, author_tuple, date, 
		              storage_location):
		self.V[version_id] = (version_id, dpyname, author_tuple, date, storage_location)

	def set_type (self, sm, cm):
		self._type = (sm, cm)

	def set_brid (self, a_brid):
		self.brid = a_brid

	def set_prop (self, n, v, st='string', ct='string', user='*'):
		self.saved_properties += """\
<property name="%s" simple-type="%s" complex-type="%s">
	%s
</property>
		""" % (n, st, ct, v) # TODO account for user

	def putline (self, outfile, s):
		outfile.write (s)

	def push_versions (self, outfile):
		self.putline(outfile, '<versions>')
		for each in self.V.values():
			version_id, dpyname, author_tuple, date, storage_location = each
			an, ae, aip = author_tuple
			C = """\
		<version id="%s" displayname="%s">
			<author name="%s" email="%s" ipaddy="%s" />
			<submittor logon="OnetAddNewsgroupMessage2" ipaddy="127.0.0.1" date="%s" />
			<storage location="%s" />
		</version>
			""" % (version_id, dpyname, an, ae, aip, date, storage_location)
			#~ <perms><perm id="EcM001"/><perm id="EcV001"/></perms>
			self.putline(outfile, C)
		self.putline(outfile, '</versions>')

	def push_out(self, outfile):
		self.putline(outfile, '<?xml version="1.0"?>')
		self.putline(outfile, '<onet_file version="2" brid="%s">' % self.brid)
		#~ outfile.incr_tabs()
		self.putline(outfile, '<type simple-mime="image/jpeg" complex-mime="image/jpeg" />')
		self.push_versions(outfile)
		keywords, modelist, date, msgid = '', '', '', ''
		c = """
	
	<permissions order="allow, deny">
		<grant perm="class:modify" target="user:GetNews" id="EcM001" />
		<grant perm="class:view"   target="user:*"       id="EcV001" />
	</permissions>
	<keywords>%s</keywords>
	<modelist>%s</modelist>
	<properties>
	<property name="datetime" simple-type="string" complex-type="time/internet">
		%s
	</property>
	<property name="Message-ID" simple-type="string" complex-type="rfc822/message-id">
		%s
	</property>%s</properties>
	"""	% 	(keywords, modelist, date, msgid, self.saved_properties)
		self.putline(outfile, c)
		self.putline(outfile, '</onet_file>')
	
	def set_dpy_name(self, dpyname):
		self.dpyname = dpyname

#
# eof
#
