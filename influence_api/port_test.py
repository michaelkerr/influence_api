# -*- coding: utf-8 -*-
# port test #
#################

# V0.2
# Created Date: 2014/03/06
# Last Updated: 2014/03/06

### Resources ###
import networkx as nx
import StringIO

### FUNCTIONS ###


### MAIN ###
G = nx.DiGraph()
author_list = [('A', 'B', 2), ('B', 'A', 1), ('A', 'C', 4)]
G.add_weighted_edges_from(author_list)

with StringIO.StringIO() as output:
	nx.write_gexf(G, output)
	print output.getvalue()