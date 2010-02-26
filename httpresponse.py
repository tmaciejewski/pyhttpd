# httpresponse.py - this module makes server responce, basing on HttpQuery

import datetime
import mimetypes
import os.path
import subprocess

def makeResponse(query, config):

	code = 0
	miscHeaders = ''

	# is this a bad query?
	if query.badRequest == True:
		code = 400
	elif query.method not in ['GET', 'POST']:
		code = 405
	elif os.path.isdir(config.val('ServerRoot') + query.wantedPage) and query.wantedPage[-1] != '/':
		code = 301
		miscHeaders = miscHeaders + 'Location: ' + query.wantedPage + '/\r\n'

	# open file
	(code, lines) = getLinesFromFile(code, query.wantedPage, query.pageQuery, query.postContent, config)

	# we've got opened file
	response = makeCode(code) \
				+ makeDate() \
				+ makeServer(config.val('ServerName')) \
				+ makeConnection(code) \
				+ makeMIME(code, config.val('ServerRoot') + query.wantedPage, config.val('DefaultType'), config.val('Charset')) \
				+ makeContentLength(lines) \
				+ miscHeaders

	response = response + '\r\n'

	for line in lines:
		response = response + line

	return response

def getLinesFromFile(code, filename, queries, posts, config):

	if code == 0:
		try:
			file = open(config.val('ServerRoot') + filename, 'r')
			code = 200
		except IOError, (errno, strerror):
			if errno == 13:
				# forbidden
				code = 403
			elif errno == 2:
				# file doesn't exist
				code = 404
			elif errno == 21:
				# it's a directory
				indexes = config.val('DirectoryIndex').split()

				# try default directory index
				for index in indexes:
					if os.path.isfile(config.val('ServerRoot') + filename + index):
						return getLinesFromFile(0, filename + index, config)

				# make directory listing?
				if config.val('DirectoryListing') == 'True':
					return (200, makeDirectoryListing(filename, config.val('ServerRoot')))
				else:
					code = 404
						
			else:
				code = 500

	# open error page
	if code != 200:
		try:
			file = open(config.val(str(code)))
		except:
			return (500, ['Error page ' + str(code) + ' is missing!\r\n'])

	if filename.endswith('.py'):
		# it's Python script
		lines = runPythonScript(file, queries, posts, config)
	else:
		lines = file.readlines()
	
	file.close()

	return (code, lines)

def makeDictFromQuery(queries):
	inits = ''
	
	if queries != None:
		# make array from queries
		list = queries.split('&')
		for q in list:
			tmp = q.split('=')
			varname = tmp[0]
			try:
				val = tmp[1]
			except:
				val = 'None'

			inits = inits + '\'' + varname  + '\' : \'' + val + '\','

	return inits


def runPythonScript(file, queries, posts, config):

	inits = '_GET = { ' + makeDictFromQuery(queries) + "}\n_POST = { " + makeDictFromQuery(posts) + "}\n"

	print inits

	script = subprocess.Popen('python', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	lines = file.readlines()
	script.stdin.write(inits)
	script.stdin.writelines(lines)
	lines = script.communicate()

	if lines[1] != None:
		return lines[1].split('\n')

	if lines[0] != None:
		return lines[0].split('\n')

	return ['Python scripts error']

def makeDirectoryListing(filename, root):
	r = '<html><head><title>Index of ' + filename + '</title><head>'
	r = r+'<body><h1>Index of ' + filename + '</h1>'

	files = os.listdir(root + filename)

	for file in files:
		r = r+'<a href="' + filename + file + '">' + file + '</a><br>'

	r = r + '</body></html>'

	return r

def makeCode(code):

	header = 'HTTP/1.1 '
	codes = { 
				200:'200 OK',
				301:'301 Moved Permanently',
				400:'400 Bad Request', 
				403:'403 Forbidden', 
				404:'404 Not Found',
				405:'405 Method Not Allowed',
				500:'500 Internal Server Error'
			 }

	try:
		header = header + codes[code]
	except:
		return header + codes[500] + '\r\n' 

	return header + '\r\n'

def makeDate():
	return 'Date: ' + datetime.datetime.now().strftime('%a, %d %h %Y %H:%M:%S GMT') + '\r\n'

def makeServer(name):
	return 'Server: ' + name + '\r\n'

def makeConnection(code):
	return 'Connection: close' + '\r\n'

def makeMIME(code, filename, default, charset):
	if code == 200:
		if os.path.isdir(filename):
			mime = 'text/html'
		else:
			if filename.endswith('.py'):
				mime = 'text/html'
			else:
				mimes = mimetypes.guess_type(filename)
				mime = mimes[0]
			
				if mime == None:
					mime = default
	else:
		mime = 'text/html'

	return 'Content-Type: ' + mime + '; charset=' + charset + '\r\n'

def makeContentLength(lines):
	length = 0
	for line in lines:
		length += len(line)
	
	return 'Content-Length: ' + str(length) + '\r\n'
