from nose.tools import *
import NAME

def setup():
	print "SETUP!"

def teardown():
	print "TEAR DOWN!"

def test_basic():
	print "I RAN!"

#TODO
#
# http://127.0.0.1:5000/metrics/influence
#
# query
#
# ?graph_url='http://192.168.1.164:7474/db/data'
# this should be checked for none, empty string, a valid link and an invalid link, random string
#
# &start_date='YYYYMMDD'
# this should be checked for a valid/invalid date, a different date format (valid/invalid), None, empty string, random string
#
#&end_date='YYYYMMDD'
#same as start date
#
#&project='AQ%20%28A%29'
#Check for valid IO project names, Penguin name, None, empty string, random strings
#
#&network='ye1.org'
#Check for valid IO subforum names, Penguin name, None, empty string, random strings
#
#&metric='pagerank'
#check for valid metrics, None, Empty, random strings
#