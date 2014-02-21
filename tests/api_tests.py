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
#
# &start_date='YYYYMMDD'
# this should be checked for a valid/invalid date, a different date format (valid/invalid), None, empty string, random string
#
#&end_date='YYYYMMDD'
#same as start date
#
# check if the start data is before the end date
#
#&project='AQ%20%28A%29'
#Check for valid IO project names, Penguin name, None, empty string, All, random strings - should be based on hashes for project, topic etc
#
#&network='ye1.org'
#Check for valid IO subforum names, Penguin name, None, empty string, random strings
#
#&metric='pagerank'
#check for valid metrics, None, Empty, random strings
#
# test the graphml format for validity
#
#Test the server
#Ensure path is present in all header files
#test for inverted datess
