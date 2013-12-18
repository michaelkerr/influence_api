# -*- coding: utf-8 -*-
# Influence API support functions #
#################

# Created Date: 2013/12/18
# Last Updated: 2013/12/18

### Resources ###
import urllib2

### Classes ###


### Functions ###
def check_if_none(req_params):
	## >Remove optional params
	del req_params['subforum']
	del req_params['topic']

	## >Ensure required parameters
	for key, value in req_params.iteritems():
		if value is None:
			return False
	return True


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