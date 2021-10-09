def getQuoted(line):
	i = 1
	ch = line[:1]
	while line[i:i + 1] != ch:
		if line[i:i - 1] == '\\':
			continue
		i = i + 1
	return line[1:i], line[i + 2:]


def SplitLine(line):
	name = ''
	value = ''
	
	if line[:1] in ('"', "'"):
		name, value = getQuoted(line)
	else:
		while line[:1] not in (' ', '\t') and len(line):
##			print line
			name = name + line[:1]
			line = line[1:]
		value = line[1:]
	
	if value[:1] in ('"', "'"):
		value = value[1:-1]
	#	else:
	#		value = value[1:]
	
	return name, value


def xSplitLine(line):
	name = ''
	value = ''
	
	if line[:1] == '"':
		name, value = getQuoted(line)
	else:
		x = 0
		while line[x:1] not in (' ', '\t') and len(line) - x:
#			name = name + line[x:1]
#			line = line[1:]
			x = x + 1
		name = line[:x - 1]
		value = line[x + 1:]
	
	if value[:1] in ('"', "'"):
		value = value[1:-1]
	#	else:
	#		value = value[1:]
	
	return name, value
