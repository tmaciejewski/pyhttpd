# pyhttpd - http daemon in python
# 
# Tomasz Maciejewski

import config
import socket
import httpquery
import httpresponse

import threading 

class ClientThread (threading.Thread):
	
	def __init__(self, sock, config):
		self.socket = sock
		self.config = config
		threading.Thread.__init__ ( self )

	def run(self):

		msg = ''

		print 'aa'
	
		# recieve headers 
		while not '\r\n\r\n' in msg:
			buf = self.socket.recv(1024)

			msg = msg+buf
			print buf

		print msg

		query = httpquery.HttpQuery(msg)

		# check if this is POST
		if query.method == 'POST':
			msg = self.socket.recv(int(query.headers['Content-Length']))
			
			print msg

			query.postContent = msg

		# get response
		response = httpresponse.makeResponse(query,self.config)

		self.socket.send(response)
		self.socket.close()

##########################################

# load configuration
config = config.Config('pyhttpd.conf')
config.showConfig()

# create sockets
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), int(config.val('Port'))))

s.listen(int(config.val('MaxConnections')))

while True:  
	(clientsocket, address) = s.accept()
	
	# start the client thread
	ClientThread(clientsocket, config).start()

