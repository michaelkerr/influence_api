# -*- coding: utf-8 -*-
# port test #
#################

# V0.2
# Created Date: 2014/03/06
# Last Updated: 2014/03/06

### Resources ###
import socket

### MAIN ##
start_port = 8080
port_occupied = True
while port_occupied is True:
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		result = sock.connect_ex(('localhost', start_port))
	except:
		print 'exception'
	if result != 0:
		## >Port is open
		port_occupied = False
		print "port open: " + str(start_port)
	else:
		## >Port is closed
		print "port closed: " + str(start_port)
		start_port += 1