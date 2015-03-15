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
from podata.DiaEdmx import EdmxEntityType, DiaObject

from mock import MagicMock, Mock


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
   
class TestEdmxTypes(unittest.TestCase):

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
 
	def tearDown(self):
		'called multiple times, after every test method'
		self.logPoint()

	@mock.patch('podata.DiaEdmx.EntityType')
	def test_edmx_assoc_set_name(self, mock_entity) :
		self.logPoint()
		mock_entity.GetAttribute.return_value = u"Test"
		diaobj = DiaObject(None, EdmxEntityType)
		assoc = EdmxEntityType("test", mock_entity, diaobj)
		assoc.set_name()
		mock_entity.GetAttribute.assert_called_with(('~','Name'))
		self.assertEqual(assoc.name, u"Test", 'The name property should now be \"Test\"')


	def test_new_edmx_entity_type(self) :
		self.logPoint()
		entity = self.files["weather"].root.DataServices.Schema[0].EntityType[0]
		
		etype = EdmxEntityType("test", entity, None, None )
		self.assertTrue(isinstance(etype, EdmxEntityType), 'The result should be an EdmxEntityType instance')
		self.assertTrue(isinstance(etype.entity, edmx.EntityType), 'The result should be an EdmxEntityType instance')
		self.assertEqual(etype.object, None, 'The object property should be None')
		self.assertEqual(etype.ns, "test", 'The ns property should be \"test\"')
		self.assertEqual(etype.entity.name, "DataPoint", 'The ns property should be \"test\"')
		
		# Not really much to do here...
		etype.create()
		
		etype.create_from_entity()
		self.assertTrue(isinstance(etype.object, DiaObject), 'The result should be an EdmxEntityType instance')
		
		etype.set_name()
		self.assertEqual(etype.name, "DataPoint", 'The name property should be \"DataPoint\"')
		self.assertEqual(etype.object.name, "DataPoint", 'The object\'s name property should be \"DataPoint\"')
		
		etype.set_type()
		self.assertEqual(etype.type, "EntityType", 'The type property should be \"EntityType\"')
		self.assertEqual(etype.object.stereotype, "EntityType", 'The object\'s type property should be \"EntityType\"')
	
		# Likewise - calls the two private functions below
		etype.create_object()

		etype._create_object_properties()
		self.assertEqual(len(etype.object.attributes), 11, 'The object should have 11 attributes')

		etype._create_object_properties()
		self.assertEqual(len(etype.object.operations), 1, 'The object should have 1 operation')
		
		# create a new entity element and set the class with it
		etype.entity = self.files["weather"].root.DataServices.Schema[0].ChildElement(edmx.EntityType)
		self.assertEqual(etype.entity.name, "Default", 'The ns property should be \"Default\"')
		
		numChildren = 0
		for child in etype.entity.GetCanonicalChildren() :
			numChildren += 1
		self.assertEqual(numChildren, 0, 'The entity should have 0 children')

		# Likewise - calls the private functions below
		#etype.update()
		
		etype.update_name()
		self.assertEqual(etype.entity.name, "DataPoint", 'The name property should be \"DataPoint\"')
		self.assertEqual(etype.name, "DataPoint", 'The name property should be \"DataPoint\"')

		etype.update_type()
		self.assertEqual(etype.type, "EntityType", 'The type property should be \"EntityType\"')

		etype._update_object_properties()
		numChildren = 0
		for child in etype.entity.Property :
			numChildren += 1
		self.assertEqual(numChildren, 11, 'The entity should now have 11 children')

		#etype._update_property(prop, value)
		#etype._clear_keys()
		etype._update_object_nav_properties()
		numChildren = 0
		for child in etype.entity.NavigationProperty :
			numChildren += 1
		self.assertEqual(numChildren, 1, 'The entity should have 1 navigation element')
		
		
	def logPoint(self):
		'utility method to trace control flow'
		callingFunction = inspect.stack()[1][3]
		currentTest = self.id().split('.')[-1]
		print 'in %s - %s()' % (currentTest, callingFunction)


if __name__ == '__main__':
	unittest.main()
