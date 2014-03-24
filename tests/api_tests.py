from nose.tools import *
import NAME

def setup():
	print "SETUP!"

def teardown():
	print "TEAR DOWN!"

def test_basic():
	print "I RAN!"

#TODO
"""
	Common tests to all endpoints
"""
""" test require api key """
"""
key=<KEY>
Check:
none
empty
valid
invalid
"""

""" test required paramaters """
"""
test start_date = 'YYYYMMDD'
check:
none
empty
a valid/invalid date (should only be in the past),
date format (valid/invalid),
"""

"""
test end_date = 'YYYYMMDD'
check:
none
empty
a valid/invalid date (should only be in the past),
date format (valid/invalid),
"""

"""
start date before end date,
start date after end date,
"""

"""
test network
check:
none given
empty,
valid (in connections)
invalid (not in connections)
"""

"""
test metric
check:
none given,
empty,
valid/invalid (in list)
"""

""" Test optional paramaters """
"""
Test subforum
check:
empty
valid/invalid
"""

"""
Test matched_project
check:
empty
valid/invalid
"""

"""
Test matched_topic
check:
empty
valid/invalid
"""

"""
Test scored_project
check:
empty
valid/invalid
"""

"""
Test scored_topic
check:
empty
valid/invalid
"""

"""
Test twit_collect
check:
empty
valid/invalid
"""

"""
Test type
check:
empty
valid/invalid
"""

""" check retired endpoints """

"""
	Test metrics/centrality
"""
""" Check valid json response """

"""
	Test graph
"""
"""
Test graph_format parameter
check:
none
empty
valid
invalid, but future
invalid
"""

"""
Test csv format
"""

"""
Test graphml format
"""

"""
Test gexf format
"""

