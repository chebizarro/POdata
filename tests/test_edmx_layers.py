import unittest
import inspect
from types import *
import time;
import cPickle as pickle
import sys
sys.path.append('../src/plugins')

import pyslet.odata2.metadata as edmx

import dia

from pudb import set_trace
from podata.DiaEdmx import DiaEdmx, EdmxLayer

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
		self.schema = self.files["metadata"].root.DataServices.Schema[0]
		self.diagram = dia.new("metadata")
		schemaName = self.schema.GetAttribute(('~','Namespace'))
		self.layer = self.diagram.data.add_layer(schemaName)
		self.logPoint()
 
	def tearDown(self):
		'called multiple times, after every test method'
		self.logPoint()

	def test_new_layer(self) :
		self.logPoint()
		
		edmxlayer = EdmxLayer(self.layer, self.diagram)
		
		self.assertTrue(isinstance(edmxlayer, EdmxLayer), 'The result should be an EdmxLayer instance')
		self.assertEqual(len(edmxlayer.objects), 0, 'The layer should have no objects')
		
	def test_add_entity(self) :
		self.logPoint()
		
		edmxlayer = EdmxLayer(self.layer, self.diagram)
		
		self.assertTrue(isinstance(edmxlayer, EdmxLayer), 'The result should be an EdmxLayer instance')
		self.assertEqual(len(edmxlayer.objects), 0, 'The layer should have no objects')
		
		newentity= self.schema.GetChildren().next()
		edmxlayer.add_entity(newentity)
		
		self.assertEqual(len(edmxlayer.objects), 1, 'The layer should have one object now')

	def test_add_schema(self) :
		self.logPoint()
		
		edmxlayer = EdmxLayer(self.layer, self.diagram)
		
		self.assertTrue(isinstance(edmxlayer, EdmxLayer), 'The result should be an EdmxLayer instance')
		self.assertEqual(len(edmxlayer.objects), 0, 'The layer should have no objects')
		#set_trace()
		edmxlayer.add_schema(self.schema)
		self.assertEqual(len(edmxlayer.objects), 37, 'The layer should have one object now')

	def test_add_schema_update(self) :
		self.logPoint()
		
		edmxlayer = EdmxLayer(self.layer, self.diagram)
		
		self.assertTrue(isinstance(edmxlayer, EdmxLayer), 'The result should be an EdmxLayer instance')
		self.assertEqual(len(edmxlayer.objects), 0, 'The layer should have no objects')

		edmxlayer.add_schema(self.schema)
		self.assertEqual(len(edmxlayer.objects), 37, 'The layer should have one object now')

		edmxlayer.update()


	def logPoint(self):
		'utility method to trace control flow'
		callingFunction = inspect.stack()[1][3]
		currentTest = self.id().split('.')[-1]
		print 'in %s - %s()' % (currentTest, callingFunction)


if __name__ == '__main__':
	unittest.main()
