# -*- coding: utf-8 -*-
# influence api #
#################

# V0.2
# Created Date: 2013/12/17
# Last Updated: 2013/03/06

### Resources ###
from bson.code import Code
from datetime import datetime
from flask import abort, Flask, jsonify, make_response, request
from functools import wraps
import inf_api_support as inf_sup
import influence as inf
import networkx as nx
from pymongo import MongoClient
import StringIO
import urllib2
from uuid import uuid4


""" MongoDB Related """
mongoclient = MongoClient('192.168.1.152', 27017)
mongo_db = mongoclient['connections']
author_collection = mongo_db['authorcons']

log_filename = 'influence_api.log'

req_param_list = ['start_date', 'end_date', 'network', 'metric']
opt_param_list = ['subforum',
		'matched_project',
		'matched_topic',
		'scored_project',
		'scored_topic',
		'twit_collect',
		'type']
graph_param_list = ['graph_format']
metric_list = ['betweenness', 'closeness', 'degree', 'eigenvector', 'in_degree', 'out_degree', 'pagerank']
user_api_keys = {
		'02f22bd5-4b3b-413c-bf51-cbcd374d76ab': {'name': 'Michael', 'group': 'admin'},
		'1ec0afaa-6f41-464c-abd2-5445e006d454': {'name': 'Matthew', 'group': 'vendorx'},
		'66c18bd0-de7d-43af-aca9-c0dfa99cff5d': {'name': 'Laura', 'group': 'vendorx'},
		'85554f77-9cc4-4812-abbc-dfbdf8dccf3a': {'name': 'Ross', 'group': 'vk'},
		'7eb6aba5-43e1-424b-af67-ee827b29c84d': {'name': 'Brent', 'group': 'vendorx'},
		'38bb8f3c-0b46-480c-b6d4-a27e461d5f2d': {'name': 'Dan', 'group': 'vendorx'},
		'd91b2fa4-1474-4e76-a807-d824fd39905d': {'name': 'Chris', 'group': 'vendorx'},
		'bdc0baa4-1923-42cc-8755-4c0fb54da200': {'name': 'Viktor', 'group': 'other'},
		'c166c55b-4125-4e1a-bd5c-23a92f6642f1': {'name': 'Aaron', 'group': 'vk'},
		'ee9f3fc1-dfe5-4f8e-af91-58f517c843d3': {'name': 'Nasir', 'group': 'vendorx'},
		'c452288e-690f-4c6b-9f9e-03dec28dc1c4': {'name': 'Min', 'group': 'vendorx'},
		'b04e097c-2653-4858-ad48-758d40880d34': {'name': 'Dwayne', 'group': 'other'},
		'0376e15a-c0a1-4647-ae98-88ab510c16da': {'name': 'David', 'group': 'vendorx'},
		'e9f04a64-8487-472e-a315-a07d00010686': {'name': 'Tim', 'group': 'other'},
		}



### Functions ###
def require_apikey(generic_function):
	""" Apikey required  - decorator function """
	# the new, post-decoration function. Note *args and **kwargs here.
	@wraps(generic_function)
	def decorated_function(*args, **kwargs):
		if request.args.get('key') and request.args.get('key') in user_api_keys.keys():
			return generic_function(*args, **kwargs)
		else:
			abort(401)
	return decorated_function


def validate_required(generic_function):
	""" Validate required parameters - decorator function """
	@wraps(generic_function)
	def validated_function(*args, **kwargs):
		for entry in req_param_list:
			if not request.args.get(entry):
				#TODO return whats missing in the 400 header
				abort(400)
		if request.args.get('metric').lower() not in metric_list:
			#TODO return whats missing in the 400 header
			abort(400)
		if int(request.args.get('start_date')) > int(request.args.get('end_date')):
			#TODO return whats missing in the 400 header
			abort(400)
		return generic_function(*args, **kwargs)
	return validated_function


def check_retired(generic_function):
	""" Checks for retired endpoints - decorator function"""
	@wraps(generic_function)
	def active_function(*args, **kwargs):
		return generic_function(*args, **kwargs)
	return active_function


## >Build the mongo query
def build_mongo_query(required_params, optional_params):
	new_query = {}
	new_query['PostDate'] = {'$gte': required_params['start_date'], '$lte': required_params['end_date']}
	new_query['Network'] = required_params['network']

	for param, value in optional_params.iteritems():
		if value is not None:
			if param is 'type':
				new_query['Type'] = optional_params['type'].capitalize()
			if param is 'twit_collect':
				new_query['Meta.sources'] = optional_params['twit_collect']
			if param is 'matched_project':
				new_query['Matching'] = {'$elemMatch': {'ProjectId': optional_params['matched_project']}}
			if param is 'subforum':
				new_query['SubForum'] = optional_params['subforum']
			if param is 'matched_topic':
				#TODO
				pass
			if param is 'scored_project':
				#TODO
				pass
			if param is 'scored_topic':
				#TODO
				pass
	return new_query


def get_params(param_request, param_list):
	""" Get the optional/format parameters """
	new_params = {}
	for entry in param_list:
		if request.args.get(entry) is not None:
			new_params[entry] = urllib2.unquote(request.args.get(entry)).replace('\'', '').lower()
		else:
			new_params[entry] = None
	return new_params


def netx_to_csv(func_graph):
	out_string = '<p>'
	for line in nx.generate_edgelist(func_graph, delimiter=','):
		""" source, target, weight """
		edge = line.replace('\'', '').replace('{weight:', '').replace('}', '').replace(' ', '')
		out_string += edge + '<br>'
	out_string += '<\p>'
	return out_string


def netx_to_json(func_graph):
	func_edge_list = []
	for line in nx.generate_edgelist(func_graph, delimiter=','):
		""" {'source':string, 'target': string, 'weight': integer} """
		edge_entry = {}
		edge = line.replace('\'', '').replace('{weight:', '').replace('}', '').replace(' ', '').split(',')
		edge_entry['source'] = edge[0]
		edge_entry['target'] = edge[1]
		edge_entry['weight'] = edge[2]
		func_edge_list.append(edge_entry)
	return func_edge_list


def raise_error(error_message, error_code):
	error_dict = {'error_message': error_message}
	error_dict['status'] = str(error_code)
	#error_dict['more_info'] = 'http://LINK_TO_DOCUMENTATION'
	inf_sup.append_to_log(log_filename, str(error_dict))
	abort(make_response(str(error_dict), error_code))
	return

### Main ###
""" Start Flask App """
app = Flask(__name__)


@app.route('/')
#TODO add browsable api in root
def info():
	available = 'Available Centrality Metrics: /metrics/centrality\n'
	return available


@app.route('/metrics/centrality')
@require_apikey
@validate_required
def centrality():
	"""
	Centrality metric endpoint.
	Custome error code(s):
		557: 'Calculation did not converge'
	"""
	#start_time = datetime.now()

	# Get the REQUIRED parameters
	req_params = get_params(request, req_param_list)

	# Get the OPTIONAL parameters
	opt_params = get_params(request, opt_param_list)

	# Build the mongo query
	mongo_query = build_mongo_query(req_params, opt_params)

	# Check if there are any matches
	if author_collection.find(mongo_query).count == 0:
		raise_error('No connections found matching the criteria', 416)
	else:
		# Map/reduce the A-->A connections
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
		# Create a unique collection based on this query
		query_collection = str(uuid4())
		try:
			a2a_result = author_collection.map_reduce(a2a_map, a2a_reduce, query_collection, query=mongo_query).find()
		except Exception as e:
			raise_error(str(e), 503)

	# Build the author list
	author_list = []
	for a2a_count in a2a_result:
		con_author = a2a_count['_id']['author'].replace('&', '&amp;')
		con_connect = a2a_count['_id']['connection'].replace('&', '&amp;')
		if (len(con_author) > 0) and (len(con_connect) > 0):
			author_list.append((con_author, con_connect, int(a2a_count['value']['count'])))

	# Delete the collection based on this query
	mongo_db[query_collection].drop()

	# Influence Calculations
	if len(author_list) > 0:
		# Create a blank graph
		G = nx.DiGraph()

		# Add the edges to the graph
		G.add_weighted_edges_from(author_list)

		# Run the requested metric, on the graph 'G'
		#TODO fix eigenvector formatting
		if req_params['metric'] == 'eigenvector':
			raise_error('No connections found matching the criteria', 501)

		calc_metric, stats = inf.run_metric(req_params['metric'], G, 'weight', True)

		if '>calc_error<' in calc_metric.keys():
			if req_params['metric'] == 'pagerank':
				# Raise custom error code - calculation did not converge
				raise_error('Pagerank did not converge', 557)
			else:
				raise_error('General calculation error', 557)
	else:
		raise_error('No connections found matching the criteria', 416)

	# Build the dictionary to return
	data_results = {}

	# Append the metric data
	data_results['metrics'] = calc_metric

	# To the log
	#TODO app.logger.debug('A value for debugging')
	#TODO Log the stats
	#statistics = {}
	#statistics['api_query'] = req_params + opt_params
	#statistics['mongo_query'] = mongo_query
	#statistics['influence_metric'] = req_params['metric']
	#statistics['metric_runtime'] = stats
	#statistics['full_runtime'] = str(datetime.now() - start_time)
	#statistics['graph_nodes'] = G.order()
	#statistics['graph_edges'] = G.size()
	#inf_sup.append_to_log(log_filename, str(statistics))

	return jsonify(result=data_results)


@app.route('/graph')
@require_apikey
@validate_required
def graph():
	"""
	Graph endpoint.
	"""
	#start_time = datetime.now()
	graph_results = {}

	# Get the required parameters
	req_params = get_params(request, req_param_list)

	#Get the OPTIONAL parameters
	opt_params = get_params(request, opt_param_list)

	# Get the GRAPH parameters
	graph_params = get_params(request, graph_param_list)

	#Build the mongo query
	mongo_query = build_mongo_query(req_params, opt_params)

	# Check if there are any matches
	if author_collection.find(mongo_query).count() == 0:
		raise_error('No connections found matching the criteria', 416)
	else:
		# Map/reduce the A-->A connections
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
		# Create a unique collection based on this query
		query_collection = str(uuid4())
		try:
			a2a_result = author_collection.map_reduce(a2a_map, a2a_reduce, query_collection, query=mongo_query).find()
		except Exception as e:
			raise_error(str(e), 503)

	# Build the author list
	author_list = []
	for a2a_count in a2a_result:
		con_author = a2a_count['_id']['author'].replace('&', '&amp;')
		con_connect = a2a_count['_id']['connection'].replace('&', '&amp;')
		if (len(con_author) > 0) and (len(con_connect) > 0):
			author_list.append((con_author, con_connect, int(a2a_count['value']['count'])))

	# Delete the collection based on this query
	mongo_db[query_collection].drop()

	if len(author_list) > 0:
		# Create a blank graph
		G = nx.DiGraph()

		# Add the edges to the graph
		G.add_weighted_edges_from(author_list)

		future_formats = ['geoff', 'gxl']
		""" To Consider: 'gml', 'XGMML', 'RDF', 'graphxml'"""
		if (graph_params['graph_format'] is None) or (graph_params['graph_format'] == 'json'):
			graph_results['graph'] = netx_to_json(G)
		elif graph_params['graph_format'] == 'gexf':
			output = StringIO.StringIO()
			nx.write_gexf(G, output)
			response = make_response(output.getvalue())
			response.headers["Content-Type"] = 'text/xml'
			return response
		elif graph_params['graph_format'] == 'graphml':
			output = StringIO.StringIO()
			nx.write_graphml(G, output)
			response = make_response(output.getvalue())
			response.headers["Content-Type"] = 'text/xml'
			return response
		elif graph_params['graph_format'] == 'csv':
			output = StringIO.StringIO()
			output.write(netx_to_csv(G))
			response = make_response(output.getvalue())
			#response.headers["Content-Type"] = 'text/txt'author_collection.find(mongo_query).count
			return response
		elif graph_params['graph_format'] in future_formats:
			raise_error('Format not currently supported, but will be in the future', 501)
		else:
			raise_error('Format not currently supported', 406)
	else:
		raise_error('Unknown graph format', 416)

	return jsonify(graph_results)


#@app.route('/authors')
#@require_apikey

#@app.route('/posts')
#@require_apikey

if __name__ == '__main__':
	app.debug = True
	app.run(processes=1, host='0.0.0.0')