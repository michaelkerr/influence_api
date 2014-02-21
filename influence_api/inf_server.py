#!/usr/bin/env python
# -*- coding: utf-8 -*-
# influence api server#
#################

# V0.1
# Created Date: 2013/02/20
# Last Updated: 2013/02/21


### Resources ###
from influence_api import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

settings = dict(ssl_options={"certfile": 'server.crt', "keyfile": 'server.key'})

if __name__ == '__main__':
		http_server = HTTPServer(WSGIContainer(app), **settings)
		http_server.listen(443)
		IOLoop.instance().start()