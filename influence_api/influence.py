# -*- coding: utf-8 -*-
# Generic Influence #
#####################

# Created Date: 2013/08/15
# Last Updated: 2013/12/19
# Version 0.5

# Resources
import networkx as nx
from datetime import datetime


# Functions
def run_metric(metric_name, G, metric_weight, use_norm):
	#print '\n>> ' + "Calculating " + metric_name
	start_time = datetime.now()
	if metric_name == 'degree':
		graph_metric = G.degree(nbunch=None, weight=metric_weight)
		normalize_metric(G, graph_metric, metric_weight)
	elif metric_name == 'in_degree':
		graph_metric = G.in_degree(nbunch=None, weight=metric_weight)
		normalize_metric(G, graph_metric, metric_weight)
	elif metric_name == 'out_degree':
		graph_metric = G.out_degree(nbunch=None, weight=metric_weight)
		normalize_metric(G, graph_metric, metric_weight)
	elif metric_name == 'closeness':
		graph_metric = nx.closeness_centrality(G, distance=None, normalized=use_norm)
		# use distance as weight? to increase importance as weight increase distance = 1/weight
	elif metric_name == 'betweenness':
		graph_metric = nx.betweenness_centrality(G, normalized=use_norm, weight=metric_weight)
	elif metric_name == 'eigenvector':
		graph_metric = nx.eigenvector_centrality_numpy(G)
	elif metric_name == 'pagerank':
		graph_metric = nx.pagerank_numpy(G, weight=metric_weight)
	end_time = datetime.now()
	stats = end_time - start_time
	#print "Calculation completed in: " + str(stats)
	return graph_metric, stats


def normalize_metric(G, graph_metric, metric_weight):
	norm_base = 0
	#if weighted, determine maximum
	if metric_weight == "weight":
		# norm base is the sum of all the weights in the graph
		norm_base = len(G)
		#for k,v in G.iteritems():
		#   norm_base += 1
	else:
		# determine number of authors (nodes) in the graph
		norm_base = len(G)
	# iterate through all items in a dictionary
	for k, v in graph_metric.iteritems():
		# divide by len(G)
		graph_metric[k] = str(format((float(graph_metric[k]) / norm_base), '0.5f'))
	return graph_metric

