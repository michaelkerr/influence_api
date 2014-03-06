# -*- coding: utf-8 -*-
# influence api server#
#################

# V0.2
# Created Date: 2013/02/20
# Last Updated: 2013/02/25


### Resources ###
from influence_api import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options

define("port", default=8080, help="Port to listen on", type=int)

### Functions ###


### Main ###
if __name__ == '__main__':
	options.parse_command_line()
	http_server = HTTPServer(WSGIContainer(app))
	http_server.listen(options.port)
	IOLoop.instance().start()