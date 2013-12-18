# -*- coding: utf-8 -*-
# influence api #
#################

# Created Date: 2013/12/17
# Last Updated: 2013/12/17

### Resources ###


from flask import Flask, Response, json, jsonify, request, Blueprint, render_template
import json
import re
import urllib2
from urlparse import urlparse

from datetime import datetime
import inf_api_support as inf_sup
import influence as inf
import networkx as nx
from py2neo import neo4j
import sys

app = Flask(__name__)


#TODO add browsable api in root


@app.route('/_api/pagerank')
def pagerank():
	## >Get the REQUIRED parameters
	req_params = {}
	req_params['graph_url'] = urllib2.unquote(request.args.get('graph_url'))
	req_params['start_date'] = urllib2.unquote(request.args.get('start_date'))
	req_params['end_date'] = urllib2.unquote(request.args.get('end_date'))
	req_params['project'] = urllib2.unquote(request.args.get('project'))
	req_params['network'] = urllib2.unquote(request.args.get('network'))
	req_params['metric'] = 'Pagerank'

	## >Get the OPTIONAL parameters
	opt_params = {}
	opt_params['subforum'] = urllib2.unquote(request.args.get('subforum'))
	opt_params['topic'] = urllib2.unquote(request.args.get('topic'))

	## >Check if any required parameters are None
	for key, value in req_params.iteritems():
		if value is None:
			ret_string = 'Required parameter missing: ' + key
			return jsonify(result=ret_string)

	## >Create DB connection
	graph_db = neo4j.GraphDatabaseService(req_params['graph_url'])

	## >Get the node index
	node_index = graph_db.get_index(neo4j.Node, "node_auto_index")

	## >Get the project node
	#TODO handle 'no project' calculations
	project_node, = node_index.get("name", project)
	if project_node is None:
		return jsonify(result='Project not in graph')

	## >Get the network node
	network_node, = node_index.get("name", network)
	if network_node is None:
		return jsonify(result='Network not in graph')

	elif not (network_node.match_outgoing(rel_type="belongs_to", end_node=project, limit=1)):
			return jsonify(result='No valid Network-->Project relationship')

	## >Get all the network-->author relationships in the graph
	network_author_rels = network_node.match_outgoing(rel_type="contains", end_node=None, limit=None)

	## >For each author in the network
	author_list = []
	for author in network_author_rels:
		## >Get the author's node data
		author_node = author.end_node

		## >Get the connection relationships for the author
		auth_con_rels = graph_db.match(start_node=author_node,
							rel_type="talks_to",
							end_node=None,
							limit=None,
							bidirectional=False)

		## >Author-Connection dictionary
		con_dict = {}

		## >For each relationship
		for con_rel in auth_con_rels:
			## >If the relationship meets the required criteria
			if ((con_rel['date'] >= start_date) and (con_rel['date'] <= end_date) and (con_rel['scored_project'] == project)):
				con_name = con_rel.end_node['name']

				## >Network level graph
				if (subforum is None) and (topic is None):
					con_dict = inf_sup.update_weights(con_rel, con_dict)

				## >If a subforum is specified (but not a topic)
				elif (subforum is not None) and (topic is None):
					if (con_rel['subforum'].encode('utf_8') == subforum):
						con_dict = inf_sup.update_weights(con_rel, con_dict)

				## >If a topic is specified (but not a subforum)
				elif (subforum is None) and (topic is not None):
					if (con_rel['topic'] == topic):
						con_dict = inf_sup.update_weights(con_rel, con_dict)

				## >If both a subforum and topic are specified
				elif ((subforum is not None) and (topic is not None)):
					if ((con_rel['subforum'].encode('utf_8') == subforum) and (con_rel['topic'] == topic)):
						con_dict = inf_sup.update_weights(con_rel, con_dict)

		## >Update the master list of (author, connection, weight) meeting the specified criteria for an author
		for k, v in con_dict.iteritems():
			author_list.append((author_node['name'], k, v))

	## >Calculate the pagerank
	return


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')


start_date = None  # '20131101'
end_date = None  # '20131131'
project = None  # 'AQ (A)'
network = None  # 'ye1.org'
metric_name = None  # 'Pagerank'
subforum = None
topic = None