# -*- coding: utf-8 -*-
# Influence API support functions #
#################

# Created Date: 2013/12/18
# Last Updated: 2013/12/19

### Resources ###
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
	filename = ''
	if params['project'] is not None:
		filename += params['project'] + '_'
	if params['network'] is not None:
		filename += params['network'] + '_'
	if params['subforum'] is not None:
		filename += params['subforum'] + '_'
	if params['topic'] is not None:
		filename += params['topic'] + '_'
	filename += str(params['start_date']) + str(params['end_date']) + '.graphml'
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