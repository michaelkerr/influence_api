# -*- coding: utf-8 -*-
# influence api server#
#################

# V0.1
# Created Date: 2013/02/20
# Last Updated: 2013/02/25


### Resources ###
import ConfigParser
from influence_api import app
#from inf_api_support import detectCPUs
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


### Functions ###
def read_config(section):
	config_dict = {}
	options = config.options(section)
	for option in options:
		config_dict[option] = config.get(section, option)
	return config_dict

### Main ###
config = ConfigParser.ConfigParser()
config.read("inf_config.ini")
config_sections = config.sections()

cert_name = read_config('SERVER')['certfile']
key_name = read_config('SERVER')['keyfile']
base_port = read_config('SERVER')['baseport']
settings = dict(ssl_options={"certfile": cert_name, "keyfile": key_name})

## >Get the number of processors
#num_processors = detectCPUs()

## >If the number of processors is >2
#if num_processors > 2:
	### >Create n-2 tornado servers
	#num_processors -= 2


if __name__ == '__main__':
	http_server = HTTPServer(WSGIContainer(app), **settings)
	http_server.listen(443)
	#http_server = HTTPServer(WSGIContainer(app))
	#http_server.listen(base_port)
	IOLoop.instance().start()