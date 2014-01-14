# -*- coding: utf-8 -*-
# influence api #
#################

# V0.2
# Created Date: 2013/12/17
# Last Updated: 2013/12/19

### Resources ###
from flask import Flask, jsonify, request, make_response
import urllib2

#from datetime import datetime
import HTMLParser
import inf_api_support as inf_sup
import influence as inf
import networkx as nx
from py2neo import neo4j

app = Flask(__name__)

#TODO put these in a configuration file
#TODO TEST graphml support
req_param_list = ['graph_url', 'start_date', 'end_date', 'project', 'network', 'metric', 'return_graph']
opt_param_list = ['subforum', 'topic', 'format']
metric_list = ['betweenness', 'closeness', 'degree', 'eigenvector', 'in_degree', 'out_degree', 'pagerank']
valid_urls = ['http://192.168.1.164:7474/db/data']

#TODO add browsable api in root


@app.route('/')
def info():
	available = 'Available Centrality Metrics: /metrics/centrality\n'
	return available


@app.route('/metrics/centrality')
def centrality():
	#TODO add config file read
	#TODO support cross network calculations (author_node --is--> author_node)
	## >Get the REQUIRED parameters
	req_params = {}
	for entry in req_param_list:
		if request.args.get(entry) is not None:
			req_params[entry] = urllib2.unquote(request.args.get(entry)).replace('\'', '')
		else:
			ret_string = 'Required parameter missing: ' + entry
			return jsonify(result=ret_string)

	## >Get the OPTIONAL parameters
	opt_params = {}
	for entry in opt_param_list:
		if request.args.get(entry) is not None:
			opt_params[entry] = urllib2.unquote(request.args.get(entry)).replace('\'', '')
		else:
			opt_params[entry] = None

	params = dict(req_params.items() + opt_params.items())
	params['start_date'] = int(params['start_date'])
	params['end_date'] = int(params['end_date'])

	## >Create DB connection
	if req_params['graph_url'].replace('\'', '') not in valid_urls:
		ret_string = 'Invalid graph URL'
		return jsonify(result=ret_string)

	graph_db = neo4j.GraphDatabaseService(params['graph_url'])

	## >Get the node index
	node_index = graph_db.get_index(neo4j.Node, "node_auto_index")

	## >Get the project node
	#TODO handle 'no project' and 'ALL' projects
	project_node, = node_index.get("name", params['project'])
	if project_node is None:
		return jsonify(result='Project not in graph')

	## >Get the network node
	#TODO handle 'ALL' networks
	network_node, = node_index.get("name", params['network'])
	if network_node is None:
		return jsonify(result='Network not in graph')

	elif not (network_node.match_outgoing(rel_type="belongs_to", end_node=params['project'], limit=1)):
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
			#TODO thread this
			## >If the relationship meets the required criteria

			if (int((con_rel['date']) >= int(params['start_date'])) and
				(int(con_rel['date']) <= int(params['end_date'])) and
				(con_rel['scored_project'] == params['project'])):
				#con_name = con_rel.end_node['name']

				## >Network level graph
				if (params['subforum'] is None) and (params['topic'] is None):
					con_dict = inf_sup.update_weights(con_rel, con_dict)

				## >If a subforum is specified (but not a topic)
				elif (params['subforum'] is not None) and (params['topic'] is None):
					if (con_rel['subforum'].encode('utf_8') == params['subforum']):
						con_dict = inf_sup.update_weights(con_rel, con_dict)

				## >If a topic is specified (but not a subforum)
				elif (params['subforum'] is None) and (params['topic'] is not None):
					if (con_rel['topic'] == params['topic']):
						con_dict = inf_sup.update_weights(con_rel, con_dict)

				## >If both a subforum and topic are specified
				elif ((params['subforum'] is not None) and (params['topic'] is not None)):
					if ((con_rel['subforum'].encode('utf_8') == params['subforum']) and
						(con_rel['topic'] == params['topic'])):
						con_dict = inf_sup.update_weights(con_rel, con_dict)

		## >Update the master list of (author, connection, weight) meeting the specified criteria for an author
		for k, v in con_dict.iteritems():
			author_list.append((author_node['name'], k, v))

	## >Influence Calculations
	if len(author_list) > 0:
		## >Create a black graph
		G = nx.DiGraph()

		## >Add the endges to the graph
		G.add_weighted_edges_from(author_list)

		## >Check for a valid metric name
		if params['metric'] in metric_list:
			## >Run the requested metric, on the graph 'G'
			calc_metric, stats = inf.run_metric(params['metric'], G, 'weight', True)
			#TODO REMOVE THIS - DUBUG ONLY
			inf_sup.append_to_file('test.txt', calc_metric, params['project'], params['network'], params['subforum'], params['topic'])
		else:
			return jsonify(result='Invalid metric requested')
	else:
		return jsonify(result='Parameters produced no graph/metrics')

	## >Build the dictionary to return
	data_results = {}

	## >Append the metric data
	data_results['metrics'] = calc_metric

	## >If graph requested
	if params['return_graph'].lower() == 'true':
		## >If format = data
		if params['format'] is None:
			## >Append the graph data
			data_results['graph'] = nx.to_edgelist(G, nodelist=None)
		## >If format = graphml
		elif params['format'].lower() == 'graphml':
			## >Create the graphml
			graphml_name = inf_sup.create_filename(params)
			graphml_data = '\n'.join(nx.generate_graphml(G))
			graphml_final = '<?xml version="1.0" encoding="UTF-8"?>' + "\n"
			h = HTMLParser.HTMLParser()
			for line in graphml_data.split('>'):
				line = h.unescape(line)
				graphml_final += line + '>'
				## >Get the node name
				if 'node id' in line:
					node_name = line.partition('"')[-1].rpartition('"')[0]
					print node_name
				if '<key' in line:
					graphml_final += '\n' + '  <key attr.name="' + params['metric'] + '" attr.type="double" for="node" id="d1" />'
				if 'node id=' in line:
					graphml_final += "\n" + '      <data _key="d1">' + str(calc_metric[node_name]) + '</data>'
			graphml_final = graphml_final.replace('>>', '>')
			with open('graphml_test.graphml', 'w') as output_file:
				for line in graphml_final:
					output_file.write(line.encode('utf-8'))
			if not output_file.closed:
				output_file.close()

			#nx.write_graphml(G, graphml_name)
			response = make_response(graphml_final)
			response.headers["Content-Type"] = 'text/xml'
			response.headers["Content-Distribution"] = 'attachment; filename=%s' % (graphml_name,)
			## >Add the influence metric to the graph
			## >Return the file
			return response

	## >Add the query parameters
	#TODO REMOVE - Debug only
	if app.debug is True:
		data_results['query'] = params
		#data_results['stats'] =
	return jsonify(result=data_results)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')



'''
http://127.0.0.1:5000/metrics/centrality?
graph_url=%27http://192.168.1.164:7474/db/data%27&
start_date=%2720131101%27&
end_date=%2720131107%27&
project=%27AQ%20%28A%29%27&
network=%27ye1.org%27&
metric=%27pagerank%27&
return_graph=%27true%27&
format=%27graphml%27

G=nx.path_graph(3)
bb=nx.betweenness_centrality(G)
nx.set_node_attributes(G,'betweenness',bb)

'''