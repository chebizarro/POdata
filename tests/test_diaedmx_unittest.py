import unittest
import inspect
from types import *
import time;
import cPickle as pickle
import sys
sys.path.append('../src/plugins')

import pyslet.odata2.metadata as edmx
import pyslet.odata2.csdl as edm

import dia

from pudb import set_trace
from podata.DiaEdmx import DiaEdmx

from lxml.etree import parse, XSLT, tostring, XMLParser
from utils.xmldiff import diff_xml

def logPoint(context):
	'utility function used for module functions and class methods'
	callingFunction = inspect.stack()[1][3]
	print 'in %s - %s()' % (context, callingFunction)

def setUpModule():
	'called once, before anything else in this module'
	logPoint('module %s' % __name__)

def tearDownModule():
	'called once, after everything else in this module'
	logPoint('module %s' % __name__)
   
class TestPodata(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		'called once, before any tests'
		logPoint('class %s' % cls.__name__)
		cls.files = {}
		xml = "xml/WeatherSchema.xml"
		doc = edmx.Document()
		with open(xml) as f:
			doc.Read(f)
		cls.files["weather"] = doc
		xml = "xml/metadata.xml"
		doc = edmx.Document()
		with open(xml) as f:
			doc.Read(f)
		cls.files["metadata"] = doc
		
	@classmethod
	def tearDownClass(cls):
		'called once, after all tests, if setUpClass successful'
		logPoint('class %s' % cls.__name__)
 
	def setUp(self):
		'called multiple times, before every test method'
		self.logPoint()
		self.dia = {}
		self.dia["weather"] = DiaEdmx("WeatherSchema", doc=self.files["weather"])
		self.dia["metadata"] = DiaEdmx("WeatherSchema", doc=self.files["metadata"])
 
	def tearDown(self):
		'called multiple times, after every test method'
		self.logPoint()

	def test_add_document(self) :
		self.logPoint()

	def test_show(self) :
		self.logPoint()
		self.dia["weather"].show()
		self.dia["metadata"].show()

	def test_update(self) :
		self.logPoint()
		self.dia["weather"].update()
		self.dia["metadata"].update()
		
	def test_save(self) :
		self.logPoint()
		self.dia["weather"].diagram.save("output/test_weather_save.p")
		self.dia["metadata"].diagram.save("output/test_metadata_save.p")

	def test_load(self) :
		self.logPoint()
		diagram = dia.load("output/test_weather_save.p")
		edmxnew = DiaEdmx("test_load", diagram.data)

	def test_export(self) :
		self.logPoint()
		diagram = dia.load("output/test_weather_save.p")
		edmxnew = DiaEdmx("test_load", diagram.data)
		edmxnew.update()
		edmxnew.save("output/test_weather.xml")
		diff_xml("xml/WeatherSchema.xml", "output/test_weather.xml", "output/test_weather.diff")

	def logPoint(self):
		'utility method to trace control flow'
		callingFunction = inspect.stack()[1][3]
		currentTest = self.id().split('.')[-1]
		print 'in %s - %s()' % (currentTest, callingFunction)


if __name__ == '__main__':
	unittest.main()
