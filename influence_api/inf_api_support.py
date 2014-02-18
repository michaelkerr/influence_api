# -*- coding: utf-8 -*-
# Influence API support functions #
#################

# Created Date: 2013/12/18
# Last Updated: 2013/12/19

### Resources ###
from datetime import datetime
import urllib2

### Classes ###


### Functions ###
def append_to_file(fileout, graph_metric, proj_name, net_name, sub_name, top_name):
	with open(fileout, 'a') as output_file:
		for key, value in graph_metric.iteritems():
			write_string = key.encode('utf_8') + ', ' + str(value).encode('utf_8') + '\n'
			output_file.write(write_string)
	if not output_file.closed:
		output_file.close()
	return


def append_to_log(filename, input_string):
	with open(filename, 'a') as output_file:
		output_string = str(datetime.now()) + ' >>> ' + input_string
		output_file.write(output_string.encode('utf-8'))
	if not output_file.closed:
		output_file.close()


def check_if_none(req_params):
	## >Remove optional params
	del req_params['subforum']
	del req_params['topic']

	## >Ensure required parameters
	for key, value in req_params.iteritems():
		if value is None:
			return False
	return True


def create_filename(params):
	filename = str(params['start_date']) + '_' + str(params['end_date']) + '_' + params['network'] + '_' + params['metric']
	if ('type' in params.keys()) and (params['type'] is not None):
		filename == '_' + params['type']
	if ('twit_collect' in params.keys()) and (params['twit_collect'] is not None):
		filename == '_' + params['twit_collect']
	if ('matched_project' in params.keys()) and (params['matched_project'] is not None):
		filename += '_' + params['matched_project']
	if ('scored_project' in params.keys()) and (params['scored_project'] is not None):
		filename += '_' + params['scored_project']
	if ('matched_topic' in params.keys()) and (params['matched_topic'] is not None):
		filename += '_' + params['matched_topic']
	if ('scored_topic' in params.keys()) and (params['scored_topic'] is not None):
		filename += '_' + params['scored_topic']
	filename += '.graphml'
	return filename


def get_parameters(request):
	## >Get the REQUIRED parameters
	param_dict = {}
	param_dict['graph_url'] = urllib2.unquote(request.args.get('graph_url'))
	param_dict['start_date'] = urllib2.unquote(request.args.get('start_date'))
	param_dict['end_date'] = urllib2.unquote(request.args.get('end_date'))
	param_dict['project'] = urllib2.unquote(request.args.get('project'))
	param_dict['network'] = urllib2.unquote(request.args.get('network'))

	## >Get the OPTIONAL parameters
	param_dict = {}
	param_dict['subforum'] = urllib2.unquote(request.args.get('subforum'))
	param_dict['topic'] = urllib2.unquote(request.args.get('topic'))
	return param_dict


def update_weights(connect_rel, updated_dict):
	if connect_rel.end_node['name'] in updated_dict:
		updated_dict[connect_rel.end_node['name']] += 1
	else:
		updated_dict[connect_rel.end_node['name']] = 1
	return updated_dict