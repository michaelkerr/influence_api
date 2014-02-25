# -*- coding: utf-8 -*-
# influence api #
#################

# V0.4
# Created Date: 2013/12/17
# Last Updated: 2013/02/20

### Resources ###
from bson.code import Code
import ConfigParser
from datetime import datetime
from flask import abort, Flask, jsonify, make_response, request
from functools import wraps
import HTMLParser
import inf_api_support as inf_sup
import influence as inf
import networkx as nx
from pymongo import MongoClient
import urllib2
from uuid import uuid4

log_filename = 'influence_api.log'

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
		'e9f04a64-8487-472e-a315-a07d00010686': {'name': 'John', 'group': 'vk'}
		}


### Functions ###

## >Apikey required decorator function
def require_apikey(generic_function):
	# the new, post-decoration function. Note *args and **kwargs here.
	def decorated_function(*args, **kwargs):
		#TODO store this somewhere else, generate for others
		if request.args.get('key') and request.args.get('key') in user_api_keys.keys():
			return generic_function(*args, **kwargs)
		else:
			abort(401)
	return decorated_function


## >Build the mongo query
def build_mongo_query(required_params, optional_params):
	new_query = {}
	new_query['PostDate'] = {'$gte': required_params['start_date'], '$lte': required_params['end_date']}
	new_query['Network'] = required_params['network']

	for param, value in optional_params.iteritems():
		if value is not None:
			if param is 'type':
				new_query['Type'] = optional_params['type']
			if param is 'twit_collect':
				new_query['Meta.sources'] = {'$in': [optional_params['twit_collect']]}
			if param is 'matched_project':
				new_query['Matching'] = {'$elemMatch': {'ProjectId': optional_params['matched_project']}}
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


def create_filename(file_params):
	filename = str(file_params['start_date']) + '_' + str(file_params['end_date']) + '_' + file_params['network'] + '_' + file_params['metric']
	if ('type' in file_params.keys()) and (file_params['type'] is not None):
		filename == '_' + file_params['type']
	if ('twit_collect' in file_params.keys()) and (file_params['twit_collect'] is not None):
		filename == '_' + file_params['twit_collect']
	if ('matched_project' in file_params.keys()) and (file_params['matched_project'] is not None):
		filename += '_' + file_params['matched_project']
	if ('scored_project' in file_params.keys()) and (file_params['scored_project'] is not None):
		filename += '_' + file_params['scored_project']
	if ('matched_topic' in file_params.keys()) and (file_params['matched_topic'] is not None):
		filename += '_' + file_params['matched_topic']
	if ('scored_topic' in file_params.keys()) and (file_params['scored_topic'] is not None):
		filename += '_' + file_params['scored_topic']
	filename += '.graphml'
	return filename


## >Get the optional/format parameters
def get_params(param_request, param_list):
	new_params = {}
	for entry in param_list:
		if request.args.get(entry) is not None:
			new_params[entry] = urllib2.unquote(request.args.get(entry)).replace('\'', '')
		else:
			new_params[entry] = None
	return new_params


def read_config(section):
	config_dict = {}
	options = config.options(section)
	for option in options:
		config_dict[option] = config.get(section, option)
	return config_dict


def read_config_list(section):
	config_dict = {}
	options = config.options(section)
	for option in options:
		config_dict[option] = config.get(section, option).split(',')
	return config_dict


## >Validate required parameters
def validate_required(validate_request):
	#TODO add config file read
	validated_params = {}
	for entry in req_param_list:
		if validate_request.args.get(entry) is not None:
			validated_params[entry] = urllib2.unquote(request.args.get(entry)).replace('\'', '')
		else:
			ret_string = {'error': 'Required parameter missing: ' + entry}
			inf_sup.append_to_log(log_filename, str(ret_string))
			return ret_string
	## >Verify the metric is valid
	if validated_params['metric'].lower() not in metric_list:
		ret_string = {'error': 'Invalid metric requested'}
		inf_sup.append_to_log(log_filename, str(ret_string))
		return ret_string
	## >Verify the start date is before the end date
	if int(validated_params['start_date']) > int(validated_params['end_date']):
		ret_string = {'error': 'End data before start date'}
		inf_sup.append_to_log(log_filename, str(ret_string))
		return ret_string
	return validated_params


### Main ###
## >Config related
config = ConfigParser.ConfigParser()
config.read("inf_config.ini")
config_sections = config.sections()

### >MongoDB
mongo_ip = read_config('Database')['mongoip']
mongo_port = int(read_config('Database')['mongoport'])
mongoclient = MongoClient(mongo_ip, mongo_port)
mongoclient = MongoClient('192.168.1.152', 27017)
mongo_db = mongoclient['connections']
author_collection = mongo_db['authorcons']

### >Parameters
req_param_list = read_config_list('Parameters')['req_param_list']
opt_param_list = read_config_list('Parameters')['opt_param_list']
format_param_list = read_config_list('Parameters')['format_param_list']
metric_list = read_config_list('Parameters')['metric_list']


## >Start Flask App
app = Flask(__name__)


#TODO add browsable api in root
@app.route('/')
def info():
	available = 'Available Centrality Metrics: /metrics/centrality\n'
	return available


#@app.route('/graph')
#def graph():
	## >Get the REQUIRED parameters
	## >Verify the metric is valid
	## >Verify the start date is before the end date
	## >Get the OPTIONAL parameters
	## >Get the FORMAT parameters
	## >Build the mongo query
	## >Check if there are any matches
	## >Build the author list
	## >If JSON requested
	## >If graph requested
	## >return the graph


@app.route('/metrics/centrality')
@require_apikey
def centrality():
	start_time = datetime.now()
	#TODO add config file read
	#TODO support cross network calculations (author_node --is--> author_node)
	## >Get the REQUIRED parameters
	req_params = validate_required(request)
	if 'error' in req_params.keys():
		return jsonify(req_params)

	## >Get the OPTIONAL parameters
	opt_params = get_params(request, opt_param_list)

	## >Get the FORMAT parameters
	for_params = get_params(request, format_param_list)

	params = dict(req_params.items() + opt_params.items())

	## >Build the mongo query
	mongo_query = build_mongo_query(req_params, opt_params)

	## >Check if there are any matches
	if author_collection.find(mongo_query).count == 0:
		ret_string = {'error': 'No connections found matching the criteria'}
		inf_sup.append_to_log(log_filename, str(ret_string))
		return jsonify(ret_string)
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
		## >Create a unique collection based on this query
		query_collection = str(uuid4())
		a2a_result = author_collection.map_reduce(a2a_map, a2a_reduce, query_collection, query=mongo_query).find()

	## >Build the author list
	author_list = []
	for a2a_count in a2a_result:
		con_author = a2a_count['_id']['author'].replace('&', '&amp;')
		con_connect = a2a_count['_id']['connection'].replace('&', '&amp;')
		if (len(con_author) > 0) and (len(con_connect) > 0):
			author_list.append((con_author, con_connect, int(a2a_count['value']['count'])))

	## >Delete the collection based on this query
	mongo_db[query_collection].drop()

	## >Influence Calculations
	if len(author_list) > 0:
		## >Create a black graph
		G = nx.DiGraph()

		## >Add the endges to the graph
		G.add_weighted_edges_from(author_list)

		## >Run the requested metric, on the graph 'G'
		try:
			calc_metric, stats = inf.run_metric(params['metric'], G, 'weight', True)
		except:
			if params['metric'] is 'pagerank':
				calc_metric, stats = inf.run_metric('pagerank_norm', G, 'weight', True)
				if '>calc_error<' in calc_metric.keys():
					return jsonify({'error': 'Pagerank did not converge'})
	else:
		ret_string = {'error': 'No connections found matching the criteria'}
		inf_sup.append_to_log(log_filename, str(ret_string))
		return jsonify(ret_string)

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
				graphml_name = create_filename(params)
				## >Get the graphml data
				graphml_data = '\n'.join(nx.generate_graphml(G))
				## >Add the versioning
				graphml_final = '<?xml version="1.0" encoding="UTF-8"?>' + "\n" + '<!--'
				for key, value in params.iteritems():
					if value is not None:
						graphml_final += key + ': ' + value + ', '
				graphml_final += '-->'
				h = HTMLParser.HTMLParser()

				for line in graphml_data.split("\n"):
					## >Escape the html content
					line = h.unescape(line)
					## >For each node add appropriate metric data into the graphml
					if '<node id="' in line:
						graphml_final += (line.replace('/>', '>') + "\n")
						node_name = line.partition('"')[-1].rpartition('"')[0]
						if (node_name is None) or(node_name is ''):
							graphml_final += '      <data key="d1">' + 'NODE NAME ERROR' + '</data>' + "\n"
						else:
							graphml_final += '      <data key="d1">' + str(calc_metric[node_name]) + '</data>' + "\n"
						graphml_final += '    </node>' + "\n"
					else:
						graphml_final += line + "\n"
						## >Add the key for the metric attribute
						if '<key' in line:
							graphml_final += '  <key attr.name="' + params['metric'] + '" attr.type="float" for="node" id="d1" />'

				if app.debug is True:
					## >Write out the graphml for testing
					graphml_name = create_filename(params)
					with open(graphml_name, 'w') as output_file:
						for line in graphml_final:
							output_file.write(line.encode('utf-8'))
					if not output_file.closed:
						output_file.close()

				## >Create the appropriate response to return the graphml
				response = make_response(graphml_final)
				response.headers["Content-Type"] = 'text/xml'
				response.headers["Content-Disposition"] = 'attachment; filename=' + graphml_name
				return response
				#return send_file(response, attachment_filename=graphml_name, as_attachment=True)

	## >To the log
	#TODO app.logger.debug('A value for debugging')
	statistics = {}
	statistics['api_query'] = params
	statistics['mongo_query'] = mongo_query
	statistics['influence_metric'] = params['metric']
	statistics['metric_runtime'] = stats
	statistics['full_runtime'] = str(datetime.now() - start_time)
	statistics['graph_nodes'] = G.order()
	statistics['graph_edges'] = G.size()
	inf_sup.append_to_log(log_filename, str(statistics))

	if app.debug is True:
		print statistics['metric_runtime']
		### >Write out the influence for testing
		graphml_name = create_filename(params)
		influence_file = graphml_name.replace('.graphml', '.txt')
		with open(influence_file, 'w') as output_file:
			graph_list = calc_metric.items()
			for item in graph_list:
				output_file.write(item[0].encode('utf_8') + "," + str(item[1]) + '\n')
		if not output_file.closed:
			output_file.close()

	return jsonify(result=data_results)

if __name__ == '__main__':
	app.debug = True
	app.run(processes=6, host='0.0.0.0')