# -*- coding: utf-8 -*-
# influence api #
#################

# V0.2
# Created Date: 2013/12/17
# Last Updated: 2013/02/16

### Resources ###
from datetime import datetime
from flask import Flask, jsonify, request, make_response
import HTMLParser
import inf_api_support as inf_sup
import influence as inf
import networkx as nx
from pymongo import MongoClient
import urllib2
from bson.code import Code

## >MongoDB related
mongoclient = MongoClient('192.168.1.152', 27017)
mongo_db = mongoclient['connections']
author_collection = mongo_db['authorcons']


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
	#TODO validate the optional parameters

	## >Get the FORMAT parameters
	for_params = {}
	for entry in format_param_list:
		if request.args.get(entry) is not None:
			for_params[entry] = urllib2.unquote(request.args.get(entry)).replace('\'', '')
		else:
			for_params[entry] = None
	params = dict(req_params.items() + opt_params.items() + for_params.items())

	## >Build the mongo query
	mongo_query = {}
	mongo_query['PostDate'] = {'$gte': params['start_date'], '$lte': params['end_date']}
	mongo_query['Network'] = params['network']

	for param, value in opt_params.iteritems():
		if value is not None:
			if param is 'type':
				mongo_query['Type'] = opt_params['type']
			if param is 'twit_collect':
				mongo_query['Meta.sources'] = {'$in': [opt_params['twit_collect']]}
			if param is 'matched_project':
				mongo_query['Matching'] = {'$elemMatch': {'ProjectId': opt_params['matched_project']}}
			if param is 'matched_topic':
				#TODO
				pass
			if param is 'scored_project':
				#TODO
				pass
			if param is 'scored_topic':
				#TODO
				pass

	## >Check if there are any matches
	if author_collection.find(mongo_query).count == 0:
		return 'No connections found matching the criteria'
	else:
		## >Map/reduce the A-->A connections
		a2a_map = Code("""
				function () {
					emit({"author": this.Author, "connection": this.Connection},
						{"count": 1}
						);
					}
				""")
		a2a_reduce = Code("""
				function (key, values) {
					var count = 0;
					values.forEach(function(v) {
						count += v['count'];
						});
					return {"count": count};
				}
				""")
		a2a_result = author_collection.map_reduce(a2a_map, a2a_reduce, "a2a_results", query=mongo_query).find()

	## >Build the author list
	author_list = []
	for a2a_count in a2a_result:
		author_list.append((a2a_count['_id']['author'].replace('&', '/x26'), a2a_count['_id']['connection'].replace('&', '/x26'), int(a2a_count['value']['count'])))

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
	if for_params['return_graph'] is not None:
		if for_params['return_graph'].lower() == 'true':
			## >If format = data
			if for_params['format'] is None:
				## >Append the graph data
				data_results['graph'] = nx.to_edgelist(G, nodelist=None)
			## >If format = graphml
			elif for_params['format'].lower() == 'graphml':
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
		## >Add the mongo query used
		data_results['query'] = mongo_query
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
'''