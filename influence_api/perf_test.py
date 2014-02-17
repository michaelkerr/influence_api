# -*- coding: utf-8 -*-
# influence api #
#################

# V0.2
# Created Date: 2013/12/17
# Last Updated: 2013/12/19

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
import json

## >MongoDB related
mongoclient = MongoClient('192.168.1.152', 27017)
mongo_db = mongoclient['connections']
author_collection = mongo_db['authorcons']

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



## >Get the REQUIRED parameters
req_params = {
		'metric': 'pagerank',
		'start_date': '20140101',
		'end_date': '20140131',
		'network': 'twitter.com'
		}

## >Get the OPTIONAL parameters
opt_params = {
		'matched_project': 'GL AFG'
		}

## >Get the FORMAT parameters
for_params = {
	'return_graph': 'true',
	'format': 'graphml'
		}

params = dict(req_params.items() + opt_params.items() + for_params.items())

test_metric_list = ['pagerank_1', 'pagerank_scipy', 'pagerank_gm', 'pagerank']
test_project_list = ['GL AFG', 'Temp project', 'CBW', 'Penguin-1']

for test_project in test_project_list:
	opt_params['matched_project'] = test_project
	for test_metric in test_metric_list:
		start_time = datetime.now()
		req_params['metric'] = test_metric
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
			print 'none found'
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
			try:
				calc_metric, stats = inf.run_metric(params['metric'], G, 'weight', True)
			except:
				test = 'failed'
				calc_metric = {}
				stats = '0.00'
		else:
			print 'no authors in graph'

		## >Build the dictionary to return
		data_results = {}

		## >Append the metric data
		data_results['metrics'] = calc_metric

		## >Add statistics about the process
		statistics = {}
		statistics['runtime'] = str(datetime.now() - start_time)
		statistics['nodes'] = G.order()
		statistics['edges'] = G.size()
		data_results['stats'] = statistics

		print opt_params['matched_project'] + ', ' + req_params['metric'] + ': ' + str(data_results['stats'])

		## >Add the mongo query used
		data_results['mongo_query'] = mongo_query

		with open('performance_testing.txt', 'a') as output_file:
			output_string = str(datetime.now()) + ', ' + opt_params['matched_project'] + ', '
			output_string += req_params['metric'] + ', ' + str(data_results['stats']) + ', ' + str(data_results['mongo_query']) + '\n'
			output_file.write(output_string.encode('utf-8'))
		if not output_file.closed:
			output_file.close()

		## >If graph requested
		if ('return_graph' in for_params) and (for_params['return_graph'] is not None) and (test is not 'failed'):
			if for_params['return_graph'].lower() == 'true':
				## >If format = data
				if for_params['format'] is None:
					## >Append the graph data
					data_results['graph'] = nx.to_edgelist(G, nodelist=None)
				## >If format = graphml
				elif for_params['format'].lower() == 'graphml':
					## >Create the graphml filename
					graphml_name = opt_params['matched_project'] + '_' + req_params['metric'] + '.graphml'
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

					## >Write out the graphml for testing
					with open(graphml_name, 'w') as output_file:
						for line in graphml_final:
							output_file.write(line.encode('utf-8'))
					if not output_file.closed:
						output_file.close()
		## >Write out the graphml for testing
		json_filename = opt_params['matched_project'] + '_' + req_params['metric'] + '.txt'
		with open(json_filename, 'w') as output_file:
			output_file.write(str(data_results).encode('utf-8'))
		if not output_file.closed:
			output_file.close()
