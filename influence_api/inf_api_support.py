# -*- coding: utf-8 -*-
# Influence API support functions #
#################

# Created Date: 2013/12/18
# Last Updated: 2013/12/20

### Resources ###
from datetime import datetime
from uuid import uuid4


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
		output_string = str(datetime.now()) + ' >>> ' + input_string + '\n'
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


def generate_api_key():
	#TODO generate based on other TBD principles
	new_key = uuid4()
	print new_key
	#TODO check if key exists
	return new_key