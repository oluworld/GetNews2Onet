
def load (klazz):
	# <begin_whoa>
	mm = __import__('AppWorks.Invocation.'+klazz)
	kl = mm.__dict__['Invocation'].__dict__[klazz]
	#print kl
	# </end_whoa>
	return kl
