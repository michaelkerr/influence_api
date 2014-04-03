# -*- coding: utf-8 -*-
# api_test_system.py
""" System functional testing """
#from itertools import combinations
import json
from types import *
import unittest
from urllib2 import Request, urlopen

server_ip = '127.0.0.1'
server_port = '5000'
base_url = 'http://' + server_ip + ':' + server_port + '/metrics/centrality?'
api_key = '45fd499-07be-4d92-93b3-d47f4607506d'
base_params = {'start_date': '20140301', 'end_date': '20140301', 'network': 'twitter.com',
	'metric': 'degree', 'key': '45fd499-07be-4d92-93b3-d47f4607506d'}


def build_query(query_url, query_dict):
	temp_string = query_url
	for key, value in query_dict.iteritems():
		if len(value) > 0:
			if ('project' in key) or ('topic' in key):
				temp_string += '&' + key + '=' + html_encode(value)
			else:
				temp_string += '&' + key + '=' + value
	return temp_string


def html_encode(to_encode):
	#TODO handle tha backslash
	replace_dict = {
			' ': '%20', '!': '%21', '#': '%22', '$': '%24', '%': '%25', '&': '%26', '"': '%27',
			'(': '%28', ')': '%29', '*': '%2A', '+': '%2B', ',': '%2C', '-': '%2D', '.': '%2E',
			'/': '%2F', '[': '%5B', '[': '%5', '^': '%5E', '-': '%5F', '`': '%60',
			'{': '%7B', '|': '%7C', '}': '%7D', '~': '%7E'
			}
	encoded = ''
	for entry in to_encode:
		if entry in replace_dict.keys():
			encoded += replace_dict[entry]
		else:
			encoded += entry
	return encoded


def query_api(query):
	request = Request(query)
	try:
		return urlopen(request)
	except Exception as e:
		return e


# Tests for all
class TestBasicQuery(unittest.TestCase):
	""" General API centrality query check for correct responses """
	def setUp(self):
		self.params = dict(base_params)
		self.url = str(base_url)

	def test_no_error(self):
		""" Checking API response to a valid base query, expect no HTTP no error """
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 401: UNAUTHORIZED')

	def test_valid_response(self):
		""" Checking API response to a valid base query, expect a valid JSON response """
		json_data = json.load(query_api(build_query(self.url, self.params)))
		#TODO Check for the number of entries in metrics to be > 0?
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)


class TestAPIKey(unittest.TestCase):
	""" API key tests, check for correct response """
	def setUp(self):
		self.params = dict(base_params)
		self.url = str(base_url)

	def test_key_missing(self):
		""" Checking API response for no key present """
		del self.params['key']
		self.assertEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 401: UNAUTHORIZED')

	def test_empty_key(self):
		""" Checking API response for empty key """
		self.params['key'] = ''
		self.assertEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 401: UNAUTHORIZED')


class TestRequiredParameters(unittest.TestCase):
	""" Required parameter tests, check for correct response"""
	def setUp(self):
		self.params = dict(base_params)
		self.url = str(base_url)

	def test_missing_start(self):
		""" Checking API response for missing start_date """
		del self.params['start_date']
		self.assertEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	def test_missing_end(self):
		""" Checking API response for missing end_date """
		del self.params['end_date']
		self.assertEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	def test_missing_network(self):
		""" Checking API response for missing network """
		del self.params['network']
		self.assertEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	def test_missing_metric(self):
		""" Checking API response for missing metric """
		del self.params['metric']
		self.assertEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	def test_invalid_metric(self):
		""" Checking API response for invalid metric """
		self.params['metric'] = 'test_metric'
		self.assertEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	def test_reversed_dates(self):
		""" Checking API response for end_date before start_date """
		self.params['start_date'] = '20140302'
		self.params['end_date'] = '20140301'
		self.assertEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')


class TestOptional(unittest.TestCase):
	""" Centrality, optional parameter tests """
	#TODO compress these into reusable components
	def setUp(self):
		self.params = dict(base_params)
		self.url = str(base_url)

	def test_matched_project_HTTP(self):
		""" Checking API response for valid matched project response, expect no HTTP errors """
		self.params['matched_project'] = 'CBW'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	def test_matched_project_JSON(self):
		""" Checking API response for valid matched project response, expect valid JSON """
		self.params['matched_project'] = 'CBW'
		print self.params
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_matched_topic_HTTP(self):
		""" Checking API response for valid matched topic response, expect no HTTP errors """
		#TODO Pick GCC topic to test against
		self.params['matched_topic'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_matched_topic_JSON(self):
		""" Checking API response for valid matched topic response, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['matched_topic'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_scored_project_HTTP(self):
		""" Checking API response for valid scored project, expect no HTTP errors """
		#TODO Pick GCC project to test against
		self.params['scored_project'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_scored_project_JSON(self):
		""" Checking API response for valid scored project, expect valid JSON """
		#TODO Pick GCC project to test against
		self.params['scored_project'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_scored_topic_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC topic to test against
		self.params['scored_topic'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_scored_topic_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['scored_topic'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_mp_mt_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC project and topic to test against
		self.params['matched_project'] = 'test'
		self.params['matched_topic'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_mp_mt_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['matched_project'] = 'test'
		self.params['matched_topic'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_mp_sp_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC project and topic to test against
		self.params['matched_project'] = 'test'
		self.params['scored_project'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_mp_sp_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['matched_project'] = 'test'
		self.params['scored_project'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_mp_st_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC project and topic to test against
		self.params['matched_project'] = 'test'
		self.params['scored_topic'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 401: UNAUTHORIZED')

	@unittest.skip('no data, returns 416')
	def test_mp_st_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['matched_project'] = 'test'
		self.params['scored_topic'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_mt_sp_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC project and topic to test against
		self.params['matched_topic'] = 'test'
		self.params['scored_project'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_mt_sp_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['matched_topic'] = 'test'
		self.params['scored_project'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_mt_st_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC project and topic to test against
		self.params['matched_toppic'] = 'test'
		self.params['scored_topic'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_mt_st_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['matched_toppic'] = 'test'
		self.params['scored_topic'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_sp_st_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC project and topic to test against
		self.params['scored_project'] = 'test'
		self.params['scored_topic'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_sp_st_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['scored_project'] = 'test'
		self.params['scored_topic'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_mp_mt_sp_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC project and topic to test against
		self.params['matched_project'] = 'test'
		self.params['matched_topic'] = 'test'
		self.params['scored_project'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_mp_mt_sp_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['matched_project'] = 'test'
		self.params['matched_topic'] = 'test'
		self.params['scored_project'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_mp_mt_st_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC project and topic to test against
		self.params['matched_project'] = 'test'
		self.params['matched_topic'] = 'test'
		self.params['scored_topic'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_mp_mt_st_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['matched_project'] = 'test'
		self.params['matched_topic'] = 'test'
		self.params['scored_topic'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_mp_sp_st_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC project and topic to test against
		self.params['matched_project'] = 'test'
		self.params['scored_project'] = 'test'
		self.params['scored_topic'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_mp_sp_st_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['matched_project'] = 'test'
		self.params['scored_project'] = 'test'
		self.params['scored_topic'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

	def test_mp_sp_mt_st_HTTP(self):
		""" Checking API response for valid scored topic, expect no HTTP errors """
		#TODO Pick GCC project and topic to test against
		self.params['matched_project'] = 'test'
		self.params['scored_project'] = 'test'
		self.params['matched_topic'] = 'test'
		self.params['scored_topic'] = 'test'
		self.assertNotEqual(str(query_api(build_query(self.url, self.params))), 'HTTP Error 400: BAD REQUEST')

	@unittest.skip('no data, returns 416')
	def test_mp_sp_mt_st_JSON(self):
		""" Checking API response for valid scored topic, expect valid JSON """
		#TODO Pick GCC topic to test against
		self.params['matched_project'] = 'test'
		self.params['scored_project'] = 'test'
		self.params['matched_topic'] = 'test'
		self.params['scored_topic'] = 'test'
		json_data = json.load(query_api(build_query(self.url, self.params)))
		json_data['result']['metrics'] = {}
		expected = {u'result': {u'metrics': {}}}
		self.assertEqual(json_data, expected)

# Tests for Metrics, Centrality
# All Degree metrics - test normalized and not
# Closeness, Betweenness, Pagerank test normalized and not
# Skip Eigenvector

# Check for error 416 - no results

'''
{'start_date': '20140301', 'end_date': '20140301', 'network': 'twitter.com', 'metric': 'in_degree'},
#{'start_date': '20140301', 'end_date': '20140301', 'network': 'mturkgrind.com', 'metric': 'in_degree'},
{'start_date': '20140301', 'end_date': '20140301', 'network': 'twitter.com', 'metric': 'out_degree'},
{'start_date': '20140301', 'end_date': '20140301', 'network': 'twitter.com', 'metric': 'closeness'},
{'start_date': '20140301', 'end_date': '20140301', 'network': 'twitter.com', 'metric': 'betweenness'},
#{'start_date': '20140301', 'end_date': '20140301', 'network': 'twitter.com', 'metric': 'eigenvector'},
{'start_date': '20140301', 'end_date': '20140301', 'network': 'twitter.com', 'metric': 'pagerank'}
]
'''


# Tests for Metrics, Other
# Test Twitter
# Test Forums

# Tests for Graph
