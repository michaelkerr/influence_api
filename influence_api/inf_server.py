# -*- coding: utf-8 -*-
# influence api server#
#################

# V0.1
# Created Date: 2013/02/20
# Last Updated: 2013/02/21


### Resources ###
from influence_api import app
from inf_api_support import detectCPUs
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

#TODO get cert and key filenames from config
settings = dict(ssl_options={"certfile": 'server.crt', "keyfile": 'server.key'})
base_port = 8080

## >Get the number of processors
num_processors = detectCPUs()
## >If the number of processors is >2
if num_processors > 2:
	## >Create n-2 tornado servers
	num_processors -= 2


if __name__ == '__main__':
	http_server = HTTPServer(WSGIContainer(app), **settings)
	http_server.listen(443)
	#http_server = HTTPServer(WSGIContainer(app))
	#http_server.listen(base_port)
	IOLoop.instance().start()