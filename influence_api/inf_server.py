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

host_ip = '127.0.0.1'
tornado_port = 8080
define("port", default=tornado_port, help="Port to listen on", type=int)


### Functions ###
def is_port_free(port_check):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host_ip, tornado_port))
		s.shutdown(2)
	except:
		return False
	return True


### Main ###
if __name__ == '__main__':
	#options.parse_command_line()

	http_server = HTTPServer(WSGIContainer(app))
	port_free = False
	while port_free is False:
		if is_port_free(tornado_port):
			port_free = True
			define("port", default=tornado_port, help="Port to listen on", type=int)
			http_server.listen(options.port)
		else:
			tornado_port += 1
	IOLoop.instance().start()