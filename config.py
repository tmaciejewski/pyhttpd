# config.py - simply class for configuration file
#
# Tomasz Maciejewski

class Config:
	def __init__(self, file):
		self.table = dict()
		
		file = open(file, 'r')

		for line in file:
			line = line.strip()
			if len(line) > 0 and line[0] != '#':  # jesli to nie jest komentarz
				if '=' in line:
					pair = line.split('=')
					self.table[pair[0].strip()] = pair[1].strip()
				else:
					raise Exception('Missing \'=\'')

		file.close()

	def showConfig(self):
		for name in self.table.iterkeys():
			print name, '=', self.table[name]

	def val(self, name):
		return self.table[name]
