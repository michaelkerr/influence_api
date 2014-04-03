""" influence unit test """

from nose.tools import *
from influence_api import influence
import networkx as nx
from random import randint
import unittest


def setup():
	# Create a random directed graph
	return nx.gnp_random_graph(randint(50, 150), 0.15, seed=None, directed=True)


def teardown():
	print "TEAR DOWN!"


def test_degrees():
	metric_list = ['degree', 'in_degree', 'out_degree']
	G = nx.gnp_random_graph(randint(50, 150), 0.15, seed=None, directed=True)
	for metric in metric_list:
		# Run the degree metric
		try:
			metric_data = influence.run_metric(metric, G, 'weight', False)
			print metric_data
		except Exception as e:
			# Fail on exception, print the exception and the metric its failing on
			assert False, metric + " had an exception: " + str(e)


#def test_degree_int():
	#