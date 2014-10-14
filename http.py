import SimpleHTTPServer
import SocketServer
import BaseHTTPServer
import hashlib
import httplib, traceback
import os
from os import sep, curdir
import shutil
import sys, socket
class MyHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
	
	# handle a GET request	
	def do_GET(self):
		try:
			# isolate the filename of the resource, to check for local existence
			scriptpath = os.path.dirname(os.path.abspath(__file__))
			newindex = self.path.rfind('/')
			newdir = str(scriptpath) + '/' + str(self.path[newindex+1:])
			f = open(newdir, 'r')
			print 'Cache hit'
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(f.read())
			f.close()
			return
		# file not found; redirect to origin server
		except IOError:
			res = callorigin(self.path)		
			if res.status == 200:
				self.send_response(res.status)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				self.wfile.write(res.read())
				open(str(self.path[newindex+1:]), 'wb').writelines(res.read())
				return
			else:
				self.send_error(404, 'File Not Found: %s' % self.path)

# request to origin
def callorigin(path):
	try:
		print 'Cache miss'
		connection = httplib.HTTPConnection(origin+':8080')
		connection.request("GET",path)
		response = connection.getresponse()
		return response		

	except Exception as type:
		print 'Exception raised: ', type
		traceback.print_exc(file=sys.stdout)
		sys.exit(0)

# initialize HTTP socket
def httpd(argv):
	port = argv[1]
	global origin 
	origin = argv[3]
	try:
		port = int(port)
		if port < 49152 or port > 65535:
			print("Port number should be between 49152 and 65535, inclusive")
			sys.exit(0)

		handler_class = MyHandler
		s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s1.connect(('www.google.com', 80))
		src = s1.getsockname()[0]
		s1.close()
		
		server_address = (src, port)
		srvr = BaseHTTPServer.HTTPServer(server_address, handler_class)
		srvr.serve_forever()
	except KeyboardInterrupt:
		print '\nKeyboardInterrupt detected, server shutting down'
		sys.exit(0)
	except Exception as type:
		print 'Exception raised: ', type
		traceback.print_exc(file=sys.stdout)
		sys.exit(0)
	 

if __name__ == "__main__":
	if len(sys.argv) != 5:
		print("Usage: ./httpserver -p <port> -o <origin>")
		sys.exit(0)
	elif sys.argv[1] != '-p' or sys.argv[3] != '-o':
		print("Usage: ./httpserver -p <port> -n <origin>")
		sys.exit(0)
	elif sys.argv[1] != '-p' or sys.argv[4] != 'ec2-54-85-79-138.compute-1.amazonaws.com':
		print("Enter the proper name for the origin server")
		sys.exit(0)
	else:
		httpd(sys.argv[1:])
