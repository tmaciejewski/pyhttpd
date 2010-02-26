# httpquery.py - simple class for parsing http queries
#
# Tomasz Maciejewski

class HttpQuery:
	def __init__(self, strQuery):
		self.headers = dict()
		self.badRequest = False
		self.wantedPage = None
		self.method = None
		self.protoVersion = None
		self.postContent = None

		lines = strQuery.strip().split('\r\n')

		try:
			firstLine = lines[0].split()
		
			self.method = firstLine[0]
			self.wantedPage = firstLine[1]
			self.protoVersion = firstLine[2]
		
			self.pageQuery = None
			if '?' in self.wantedPage:
				tmp = self.wantedPage.split('?', 1)
				self.wantedPage = tmp[0]

				try:
					self.pageQuery = tmp[1]
				except:
					self.pageQuery = ''

			for line in lines[1:]:
				self.parseLine(line) 

		except:
			self.badRequest = True

	def parseLine(self, line):
		splits = line.split(':',1)

		if not self.headers.has_key(splits[0]):
			self.headers[splits[0].strip()] = splits[1].strip()

if __name__ == "__main__":
	q = HttpQuery("POST /form.html HTTP/1.1\r\nReferer: http://localhost:55557/form.html\r\nContent-Length: 13\r\n\r\n")
	print q.headers
