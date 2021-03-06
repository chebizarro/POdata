import unittest
import inspect

from types import *

import pygtk
pygtk.require("2.0")

import gtk

import sys
sys.path.append('../src/plugins')

import pyslet.iso8601 as iso
import pyslet.odata2.csdl as edm
import pyslet.odata2.core as core
import pyslet.odata2.metadata as edmx


from podata import PysletTreeModel as PysletTreeModel

from pudb import set_trace

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
   
class TestXMLModel(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		'called once, before any tests'
		logPoint('class %s' % cls.__name__)
		cls.basic_xml = "/media/shared/projects/Cambridge/web/weather/WeatherSchema.xml"
		
	@classmethod
	def tearDownClass(cls):
		'called once, after all tests, if setUpClass successful'
		logPoint('class %s' % cls.__name__)
 
	def setUp(self):
		'called multiple times, before every test method'
		self.logPoint()
		self.model = PysletTreeModel.XMLTreeModel(self.basic_xml,PysletTreeModel.SETNodeIter, False)
 
	def tearDown(self):
		'called multiple times, after every test method'
		self.logPoint()

	def test_set(self) :
		self.model.set(self.basic_xml, PysletTreeModel.SETNodeIter, False)
		self.test_on_get_iter_0()
		self.test_on_get_iter_0_0()
		self.test_on_get_iter_0_0_0()
		
	def test_on_get_flags(self):
		flag = self.model.on_get_flags()
		self.assertEqual(flag, gtk.TREE_MODEL_ITERS_PERSIST, 'Tree Iters should persist')
		self.logPoint()
 
	def test_on_get_n_columns(self):
		n_columns = self.model.on_get_n_columns()
		self.assertEqual(n_columns, 4, 'The model shouldpresent 4 columns')
		self.logPoint()

	def test_on_get_column_type(self):
		c_type = self.model.on_get_column_type(0)
		self.assertEqual(c_type, IntType, 'The first column should be an IntType')
		c_type = self.model.on_get_column_type(1)
		self.assertEqual(c_type, StringType, 'The second column should be a StringType')
		c_type = self.model.on_get_column_type(2)
		self.assertEqual(c_type, StringType, 'The third column should be an StringType')
		c_type = self.model.on_get_column_type(3)
		self.assertEqual(c_type, StringType, 'The Fourth column should be an StringType')
		c_type = self.model.on_get_column_type(4)
		self.assertTrue(not c_type, 'None should returned when an out of bounds index is provided')
		c_type = self.model.on_get_column_type(-1)
		self.assertTrue(not c_type, 'None should returned when an out of bounds index is provided')
		self.logPoint()
 
	def test_on_get_iter_0(self):
		self.logPoint()
		path = (0,)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		data = self.model.get_user_data(iter)
		self.assertTrue(data, 'there should be data returned in the gtk.TreeIter')
		self.assertTrue(data.node, 'there should be a node returned in the gtk.TreeIter data')
		node = data.node
		self.assertTrue(isinstance(node, edmx.Edmx), 'The result should be a DOM Node')
		self.assertEqual(node.XMLNAME[1], "Edmx", 'The  first result should be the root Node')

	def test_on_get_iter_0_0(self):
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		data = self.model.get_user_data(iter)
		self.assertTrue(data, 'there should be data returned in the gtk.TreeIter')
		self.assertTrue(data.node, 'there should be a node returned in the gtk.TreeIter data')
		node = data.node
		#set_trace()
		self.assertTrue(isinstance(node, edmx.DataServices), 'The result should be a DOM Node')
		self.assertEqual(node.XMLNAME[1], "DataServices", 'The  first result should be the DataServices Node')

	def test_on_get_iter_0_0_0(self):
		self.logPoint()
		path = (0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		data = self.model.get_user_data(iter)
		self.assertTrue(data, 'there should be data returned in the gtk.TreeIter')
		self.assertTrue(isinstance(data.node, edm.Schema), 'The result should be a Schema Node')

	def test_on_get_iter_0_0_0_0(self):
		self.logPoint()
		path = (0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		data = self.model.get_user_data(iter)
		self.assertTrue(data, 'there should be data returned in the gtk.TreeIter')
		self.assertTrue(isinstance(data.node, edm.EntityType), 'The result should be a EntityType Node')

	def test_on_get_iter_0_0_0_1(self):
		self.logPoint()
		path = (0,0,0,1)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		data = self.model.get_user_data(iter)
		self.assertTrue(data, 'there should be data returned in the gtk.TreeIter')
		self.assertTrue(isinstance(data.node, edm.EntityType), 'The result should be a EntityType Node')

	def test_on_get_iter_0_0_0_2(self):
		self.logPoint()
		path = (0,0,0,2)
		#set_trace()
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		data = self.model.get_user_data(iter)
		self.assertTrue(data, 'there should be data returned in the gtk.TreeIter')
		self.assertTrue(isinstance(data.node, edm.Association), 'The result should be a EntityType Node')

	def test_on_get_iter_0_1(self):
		self.logPoint()
		path = (0,1)
		#set_trace()
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), NoneType, 'The result should be None')

	def test_on_get_iter_0_0_1(self):
		self.logPoint()
		path = (0,0,1)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), NoneType, 'The result should be None')

	def test_on_get_path_0(self) :
		self.logPoint()
		path = (0,)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(npath, path, 'The result should be the same path as passed to on_get_iter')

	def test_on_get_path_0_0(self) :
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(npath, path, 'The result should be the same path as passed to on_get_iter')

	def test_on_get_path_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(npath, path, 'The result should be the same path as passed to on_get_iter')

	def test_on_get_path_0_0_0_1(self) :
		self.logPoint()
		path = (0,0,0,1)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(npath, path, 'The result should be the same path as passed to on_get_iter')

	def test_on_get_path_0_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(npath, path, 'The result should be the same path as passed to on_get_iter')

	def test_on_get_path_0_0_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(npath, path, 'The result should be the same path as passed to on_get_iter')

	def test_on_get_path_0_0_0_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0,0,0,0)
		iter = self.model.on_get_iter(path)
		npath = self.model.on_get_path(iter)
		self.assertEqual(npath, None, 'The result should be None')

	def test_on_get_value_0(self) :
		self.logPoint()
		path = (0,)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		data = self.model.get_user_data(iter)
		self.assertTrue(data, 'there should be data returned in the gtk.TreeIter')
		value = self.model.on_get_value(iter,0)
		self.assertEqual(type(value), IntType, 'The first column should be an IntType')
		self.assertEqual(value, 1, 'The first column should be an Element node')
		value = self.model.on_get_value(iter,1)
		self.assertEqual(type(value), NoneType, 'The second column will usually be None')
		value = self.model.on_get_value(iter,2)
		self.assertEqual(value, "Edmx", 'The third column should be the tag')
		value = self.model.on_get_value(iter,3)
		self.assertEqual(type(value), NoneType, 'The fourth column is content, None in this case')
		# Out of range!
		value = self.model.on_get_value(iter,4)
		self.assertEqual(type(value), NoneType, 'None should returned when an out of bounds index is provided')
 
	def test_on_get_value_0_0(self) :
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		data = self.model.get_user_data(iter)
		self.assertTrue(data, 'there should be data returned in the gtk.TreeIter')
		value = self.model.on_get_value(iter,0)
		self.assertEqual(type(value), IntType, 'The first column should be an IntType')
		self.assertEqual(value, 1, 'The first column should be an Element node')
		value = self.model.on_get_value(iter,1)
		self.assertEqual(type(value), NoneType, 'The second column will usually be None')
		value = self.model.on_get_value(iter,2)
		self.assertEqual(value, "DataServices", 'The third column should be the tag')
		value = self.model.on_get_value(iter,3)
		self.assertEqual(type(value), NoneType, 'The fourth column is content, None in this case')
		value = self.model.on_get_value(iter,4)
		self.assertEqual(type(value), NoneType, 'None should returned when an out of bounds index is provided')
 
	def test_on_get_value_0_0_0(self) :
		self.logPoint()
		path = (0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		data = self.model.get_user_data(iter)
		self.assertTrue(data, 'there should be data returned in the gtk.TreeIter')
		value = self.model.on_get_value(iter,0)
		self.assertEqual(type(value), IntType, 'The first column should be an IntType')
		self.assertEqual(value, 1, 'The first column should be an Element node')
		value = self.model.on_get_value(iter,1)
		self.assertEqual(type(value), NoneType, 'The second column will usually be None')
		value = self.model.on_get_value(iter,2)
		self.assertEqual(value, "Schema", 'The third column should be the tag')
		value = self.model.on_get_value(iter,3)
		self.assertEqual(type(value), NoneType, 'The fourth column is content, None in this case')
		value = self.model.on_get_value(iter,4)
		self.assertEqual(type(value), NoneType, 'None should returned when an out of bounds index is provided')
 
	def test_on_get_value_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		data = self.model.get_user_data(iter)
		self.assertTrue(data, 'there should be data returned in the gtk.TreeIter')
		value = self.model.on_get_value(iter,0)
		self.assertEqual(type(value), IntType, 'The first column should be an IntType')
		self.assertEqual(value, 1, 'The first column should be an Attrib node')
		value = self.model.on_get_value(iter,1)
		#set_trace()
		self.assertEqual(type(value), NoneType, 'The second column will usually be None')
		value = self.model.on_get_value(iter,2)
		self.assertEqual(value, "EntityType", 'The third column should be the tag')
 
	def test_on_get_value_0_0_0_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), NoneType, 'The result should be None')
		data = self.model.on_get_value(iter,0)
		self.assertEqual(type(data), NoneType, 'The result should be None')

 	def test_on_iter_next_0(self) :
		self.logPoint()
		path = (0,)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		iter = self.model.on_iter_next(iter)
		self.assertEqual(type(iter), NoneType, 'The result should be None')

 	def test_on_iter_next_0_0(self) :
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		iter = self.model.on_iter_next(iter)
		self.assertEqual(type(iter), NoneType, 'The result should be None')

 	def test_on_iter_next_0_0_0(self) :
		self.logPoint()
		path = (0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		iter = self.model.on_iter_next(iter)
		self.assertEqual(type(iter), NoneType, 'The result should be None')

 	def test_on_iter_next_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		iter = self.model.on_iter_next(iter)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0,0,1), 'The tuples should match')

 	def test_on_iter_next_0_0_0_1(self) :
		self.logPoint()
		path = (0,0,0,1)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		iter = self.model.on_iter_next(iter)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0,0,2), 'The tuples should match')

	def test_on_iter_children_0(self) :
		self.logPoint()
		path = (0,)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		iter = self.model.on_iter_children(iter)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0), 'The tuples should match')

	def test_on_iter_children_0_0(self) :
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		iter = self.model.on_iter_children(iter)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0,0), 'The tuples should match')
		
	def test_on_iter_children_0_0_0(self) :
		self.logPoint()
		path = (0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		iter = self.model.on_iter_children(iter)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0,0,0), 'The tuples should match')

	def test_on_iter_children_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		iter = self.model.on_iter_children(iter)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(iter)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0,0,0,0), 'The tuples should match')

	def test_on_iter_has_child_0(self) :
		self.logPoint()
		path = (0,)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		children = self.model.on_iter_has_child(iter)
		self.assertTrue(children, "the node should chilluns")

	def test_on_iter_has_child_0_0(self) :
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		children = self.model.on_iter_has_child(iter)
		self.assertTrue(children, "the node should chilluns")

	def test_on_iter_has_child_0_0_0(self) :
		self.logPoint()
		path = (0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		children = self.model.on_iter_has_child(iter)
		self.assertTrue(children, "the node should chilluns")

	def test_on_iter_has_child_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		children = self.model.on_iter_has_child(iter)
		self.assertTrue(children, "the node should have chilluns")

	def test_on_iter_has_child_0_1(self) :
		self.logPoint()
		path = (0,1)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), NoneType, 'The result should be None')
		children = self.model.on_iter_has_child(iter)
		self.assertTrue(not children, "the node should not have any chilluns")

	def test_on_iter_n_children_0(self) :
		self.logPoint()
		path = (0,)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		children = self.model.on_iter_n_children(iter)
		self.assertEqual(children, 2, 'The root node should only have one child and one attrib')

	def test_on_iter_n_children_0_0(self) :
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		children = self.model.on_iter_n_children(iter)
		self.assertEqual(children, 2, 'The node should have one child and one attrib ')

	def test_on_iter_n_children_0_0_0(self) :
		self.logPoint()
		path = (0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		children = self.model.on_iter_n_children(iter)
		self.assertEqual(children, 5, 'The item node should only have 4 children')

	def test_on_iter_n_children_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		children = self.model.on_iter_n_children(iter)
		self.assertEqual(children, 15, 'The item node should have 15 children')

	def test_on_iter_n_children_0_1(self) :
		self.logPoint()
		children = self.model.on_iter_n_children(None)
		self.assertEqual(type(children), int, 'The result should be a gtk.TreeIter')
		self.assertEqual(children, 1, 'Null sets it to the number of top level rows')

	def test_on_iter_nth_child_0(self) :
		self.logPoint()
		path = (0,)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		child = self.model.on_iter_nth_child(iter, 0)
		self.assertEqual(type(child), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(child)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0), 'The tuples should match')
		
	def test_on_iter_nth_child_0_0(self) :
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		child = self.model.on_iter_nth_child(iter, 0)
		self.assertEqual(type(child), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(child)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0,0), 'The tuples should match')
		
	def test_on_iter_nth_child_0_01(self) :
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		child = self.model.on_iter_nth_child(iter, 1)
		self.assertEqual(type(child), NoneType, 'The result should be None')

	def test_on_iter_nth_child_0_0_0(self) :
		self.logPoint()
		path = (0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		child = self.model.on_iter_nth_child(iter, 0)
		self.assertEqual(type(child), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(child)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0,0,0), 'The tuples should match')
		
	def test_on_iter_nth_child_0_02(self) :
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		#set_trace()
		child = self.model.on_iter_nth_child(iter, 2)
		self.assertEqual(type(child), NoneType, 'The result should be None')

	def test_on_iter_parent_0(self) :
		self.logPoint()
		path = (0,)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		parent = self.model.on_iter_parent(iter)
		self.assertEqual(type(parent), NoneType, 'The result should be None')

	def test_on_iter_parent_0_0(self) :
		self.logPoint()
		path = (0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		parent = self.model.on_iter_parent(iter)
		self.assertEqual(type(parent), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(parent)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,), 'The tuples should match')

	def test_on_iter_parent_0_0_0(self) :
		self.logPoint()
		path = (0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		parent = self.model.on_iter_parent(iter)
		self.assertEqual(type(parent), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(parent)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0), 'The tuples should match')
		
	def test_on_iter_parent_0_0_0_0(self) :
		self.logPoint()
		path = (0,0,0,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		parent = self.model.on_iter_parent(iter)
		self.assertEqual(type(parent), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(parent)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0,0), 'The tuples should match')
		
	def test_on_iter_parent_0_0_0_1(self) :
		self.logPoint()
		path = (0,0,1,0)
		iter = self.model.on_get_iter(path)
		self.assertEqual(type(iter), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		parent = self.model.on_iter_parent(iter)
		self.assertEqual(type(parent), gtk.TreeIter, 'The result should be a gtk.TreeIter')
		npath = self.model.on_get_path(parent)
		self.assertEqual(type(npath), tuple, 'The result should be a Tuple')
		self.assertEqual(npath, (0,0,1), 'The tuples should match')
		
	def test_on_iter_parent_0_0_0_1(self) :
		self.logPoint()
		parent = self.model.on_iter_parent(None)
		self.assertEqual(type(parent), NoneType, 'The result should be None')
		

	def logPoint(self):
		'utility method to trace control flow'
		callingFunction = inspect.stack()[1][3]
		currentTest = self.id().split('.')[-1]
		print 'in %s - %s()' % (currentTest, callingFunction)


if __name__ == '__main__':
	unittest.main()
