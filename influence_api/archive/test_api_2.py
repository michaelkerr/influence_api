# -*- coding: utf-8 -*-
# influence api #
#################

# V0.2
# Created Date: 2013/12/17
# Last Updated: 2013/12/19

### Resources ###
import time
from datetime import date, timedelta
from datetime import date, datetime, timedelta
from flask import Flask, jsonify, request, make_response
import HTMLParser
import inf_api_support as inf_sup
import influence as inf
import networkx as nx
from py2neo import neo4j
import urllib2

app = Flask(__name__)

#TODO put these in a configuration file
#TODO TEST graphml support
req_param_list = ['start_date', 'end_date', 'network', 'metric']
opt_param_list = [	'subforum',
		'matched_project',
		'matched_topic',
		'scored_project',
		'scored_topic',
		'twit_collect',
		'type']
format_param_list = ['return_graph', 'format']
metric_list = ['betweenness', 'closeness', 'degree', 'eigenvector', 'in_degree', 'out_degree', 'pagerank']

#TODO allow passing of different graphurls - one for GCC one for SM1 for instance
graph_url = 'http://192.168.1.164:7474/db/data'
#valid_urls = ['http://192.168.1.164:7474/db/data']

#TODO add browsable api in root


@app.route('/')
def info():
	available = 'Available Centrality Metrics: /metrics/centrality\n'
	return available


@app.route('/metrics/centrality')
def centrality():
	start_time = datetime.now()
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

	#TODO Validate start_date, end_date
	## >Verify the metric is valid
	if req_params['metric'] not in metric_list:
		return jsonify(result='Invalid metric requested')

	## >Verify the start date is before the end date
	if int(req_params['start_date']) > int(req_params['end_date']):
		return jsonify(result='End data before start date')

	## >Get the OPTIONAL parameters
	opt_params = {}
	for entry in opt_param_list:
		if request.args.get(entry) is not None:
			opt_params[entry] = urllib2.unquote(request.args.get(entry)).replace('\'', '')
		else:
			opt_params[entry] = None
	#TODO validate the optional parameters?

	## >Get the FORMAT parameters
	for_params = {}
	for entry in format_param_list:
		if request.args.get(entry) is not None:
			for_params[entry] = urllib2.unquote(request.args.get(entry)).replace('\'', '')
		else:
			for_params[entry] = None
	#TODO validate the optional parameters?

	## >Combine the parameters
	params = dict(req_params.items() + opt_params.items() + for_params.items())

	## >Create DB connection
	graph_db = neo4j.GraphDatabaseService(graph_url)

	## >Get the node index
	node_index = graph_db.get_index(neo4j.Node, "node_auto_index")
	relationship_index = graph_db.get_index(neo4j.Relationship, "relationship_auto_index")

	## >Get the network node
	#TODO handle 'ALL' networks
	#TODO handle the case of no network node better - crashes
	network_node, = node_index.get("name", params['network'])
	if network_node is None:
		return jsonify(result='Network not in graph')
	#elif not (network_node.match_outgoing(rel_type="belongs_to", end_node=params['project'], limit=1)):
			#return jsonify(result='No valid Network-->Project relationship')

	## >Get the relationships
	con_rel_list = []
	current_date = params['start_date']
	while int(current_date) < int(params['end_date']):
		t = time.strptime(current_date, '%Y%m%d')
		current_date = (date(t.tm_year, t.tm_mon, t.tm_mday) + timedelta(1)).strftime('%Y%m%d')
		##> Get the relationships with the post dates required
		query = 'date:' + current_date
		con_rel_list.append(relationship_index.query(query))
	network_author_rels = []
	for con_rel_gen in con_rel_list:
		for con_rel in con_rel_gen:
			## >Connection must be part of the desired network
			if con_rel.start_node.match_incoming(rel_type='contains', start_node=network_node, limit=None):
				network_author_rels.append(con_rel)

	## >For each author in the network
	author_list = []
	for author_rel in network_author_rels:
		## >Get the author's node data from the rel
		author_node = author_rel.end_node

		## >Get the connection relationships for the author
		auth_con_rels = author_node.match_outgoing(rel_type="talks_to", end_node=None, limit=None)
		#auth_con_rels = graph_db.match(start_node=author_node,
							#rel_type="talks_to",
							#end_node=None,
							#limit=None,
							#bidirectional=False)

		## >Author-Connection dictionary
		con_dict = {}

		## >For each relationship
		for con_rel in auth_con_rels:
			#TODO thread this
			## >If the relationship meets the required criteria
			## >If the length of the optional parameter dict is None - just process
			if len(opt_params.keys()) == 0:
					con_dict = inf_sup.update_weights(con_rel, con_dict)
				## >Cycle through the options
			else:
				pass

		'''
			if (int((con_rel['date']) >= int(params['start_date'])) and
				(int(con_rel['date']) <= int(params['end_date']))):
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
		'''
		## >Update the master list of (author, connection, weight) meeting the specified criteria for an author
		for k, v in con_dict.iteritems():
			author_list.append((author_node['name'], k, v))
	print str(datetime.now() - start_time)
	return jsonify(dict(author_list))
	'''
	## >Influence Calculations
	if len(author_list) > 0:
		## >Create a black graph
		G = nx.DiGraph()

		## >Add the endges to the graph
		G.add_weighted_edges_from(author_list)

		## >Run the requested metric, on the graph 'G'
		calc_metric, stats = inf.run_metric(params['metric'], G, 'weight', True)

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
			## >Create the graphml filename
			graphml_name = inf_sup.create_filename(params)
			## >Get the graphml data
			graphml_data = '\n'.join(nx.generate_graphml(G))
			## >Add the versioning
			graphml_final = '<?xml version="1.0" encoding="UTF-8"?>' + "\n"
			h = HTMLParser.HTMLParser()

			for line in graphml_data.split("\n"):
				## >Escape the html content
				line = h.unescape(line)
				## >For each node add appropriate metric data into the graphml
				if '<node id="' in line:
					graphml_final += (line.replace('/>', '>') + "\n")
					node_name = line.partition('"')[-1].rpartition('"')[0]
					graphml_final += '      <data key="d1">' + str(calc_metric[node_name]) + '</data>' + "\n"
					graphml_final += '    </node>' + "\n"
				else:
					graphml_final += line + "\n"
					## >Add the key for the metric attribute
					if '<key' in line:
						graphml_final += '  <key attr.name="' + params['metric'] + '" attr.type="float" for="node" id="d1" />'

			if app.debug is True:
				## >Write out the graphml for testing
				with open(graphml_name, 'w') as output_file:
					for line in graphml_final:
						output_file.write(line.encode('utf-8'))
				if not output_file.closed:
					output_file.close()

			## >Create the appropriate response to return the graphml
			response = make_response(graphml_final)
			response.headers["Content-Type"] = 'text/xml'
			response.headers["Content-Distribution"] = 'attachment; filename=%s' % (graphml_name,)
			return response

	if app.debug is True:
		## >If debug mode add the query parameters
		data_results['query'] = params
		## >And add statistics about the process
		statistics = {}
		statistics['runtime'] = str(datetime.now() - start_time)
		data_results['stats'] = statistics
	return jsonify(result=data_results)
	'''
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
'''