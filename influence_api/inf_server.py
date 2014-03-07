# -*- coding: utf-8 -*-
# influence api server#
#################

# V0.2
# Created Date: 2013/02/20
# Last Updated: 2013/03/06


### Resources ###
from influence_api import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
import socket
from time import sleep

default_port = 8080
define("port", default=default_port, help="Port to listen on", type=int)


### Functions ###
def get_open_port(test_port):
	port_occupied = True
	while port_occupied is True:
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			result = sock.connect_ex(('localhost', test_port))
			sock.close()
		except Exception as e:
			#TODO LOG THIS
			print str(e)
		if result != 0:
			## >Port is open
			port_occupied = False
			#TODO LOG THIS
			print "port open: " + str(test_port)
		else:
			## >Port is closed
			print "port closed: " + str(test_port)
			#TODO LOG THIS
			test_port += 1
			sleep(2)
		return test_port


### Main ###
if __name__ == '__main__':
	options.parse_command_line()
	http_server = HTTPServer(WSGIContainer(app))
	## >Spawn o first open port above the default_port - useful when spawning multiple instances of the server
	#tornado_port = get_open_port(default_port)
	#define("port", default=tornado_port, help="Port to listen on", type=int)
	http_server.listen(options.port)
	IOLoop.instance().start()