import sys, socket, random, traceback

def main(argv):
	port = argv[1]
	name = argv[3]
	inputquery = ''
	
	# validate the input port
	try:
		port = int(port)
		if port < 49152 or port > 65535:
			print("Port number should be between 49152 and 65535, inclusive")
			sys.exit(0)
		

		s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s1.connect(('www.google.com', 80))
		src = s1.getsockname()[0]
		s1.close()
		
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind((src, port))
	
		# put the datagram socket created above in listening mode 	
		while 1:
			inp, sourceaddress = s.recvfrom(2048)
			inputquery = getquestion(inp)
			if inputquery != name:
				print("Error, DNS query received for incorrect name")
			else:
				response = getpacket(inp)
				s.sendto(response, sourceaddress)
	except KeyboardInterrupt:
		print '\nKeyBoardInterrupt detected, shutting server down'		
		s.close()
		sys.exit(0)
	except Exception as type:
		print 'Socket error: ', type
		traceback.print_exc(file=sys.stdout)
		sys.exit(0)
	


# get the random IP		
def getrandomip():
	addressarray = ['54.85.79.138','54.84.248.26', '54.186.185.27', 
'54.215.216.108', '54.72.143.213', '54.255.143.38', '54.199.204.174', '54.206.102.208',
'54.207.73.134']
	return addressarray[random.randint(0, len(addressarray) - 1)]
		

# construct a response packet with the IP address of a random ec2 server
def getpacket(inp):
	packet=''
	packet+=inp[:2] + '\x81\x80'
	packet+=inp[4:6] + inp[4:6] + '\x00\x00\x00\x00'   
	packet+=inp[12:]                                   
	packet+='\xc0\x0c'                                 
	packet+='\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04' 
	packet+=str.join('',map(lambda i: chr(int(i)), getrandomip().split('.')))
	return packet
		
# isolate the question from the input query to the socket
def getquestion(inp):
	qr = (ord(inp[2]) >> 3) & 15 
	v = ''
	if qr == 0:
		initial = 12
		lon = ord(inp[initial])
		while lon != 0:
			v += inp[initial+1:initial+lon+1]+'.'
			initial += lon+1	
			lon = ord(inp[initial])
	length = len(v)
	return v[:length - 1]
		
	
if __name__ == '__main__':
	if len(sys.argv) != 5:
		print("Usage: ./dnsserver -p <port> -n <name>")
		sys.exit(0)
	elif sys.argv[1] != '-p' or sys.argv[3] != '-n':
		print("Usage: ./dnsserver -p <port> -n <name>")
		sys.exit(0)
	else:
		main(sys.argv[1:])