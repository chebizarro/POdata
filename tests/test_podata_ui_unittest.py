import unittest
import inspect
from types import *
import sys
sys.path.append('../src/plugins')

import gtk.gdk

from guitest.gtktest import GtkTestCase, guistate
from guitest.utils import mainloop_handler

from pudb import set_trace

import podata_plugin

from podata import PysletTreeModel as PysletTreeModel

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
   
class TestPodata(GtkTestCase):

	@classmethod
	def setUpClass(cls):
		'called once, before any tests'
		logPoint('class %s' % cls.__name__)
		
	@classmethod
	def tearDownClass(cls):
		'called once, after all tests, if setUpClass successful'
		logPoint('class %s' % cls.__name__)
 
	def setUp(self):
		'called multiple times, before every test method'
		self.logPoint()
		#self.app = podata_plugin.Podata(True)
 
	def tearDown(self):
		'called multiple times, after every test method'
		self.logPoint()
		self.app = None

	@mainloop_handler(podata_plugin.main)
	def test_simple(self):
		#self.logPoint()
		set_trace()
		assert podata_plugin.app
		#podata_plugin.app.quit()
		#return
	test_simple = mainloop_handler(podata_plugin.main)(test_simple)

	
	def test_set(self) :
		self.logPoint()

	def test_quit(self):
		self.app = podata_plugin.Podata(True)
		self.logPoint()
		#self.app.run()
		assert guistate.level == 0
		self.app.windows['main_window'].emit('delete-event', gtk.gdk.Event(gtk.gdk.DELETE))
		#set_trace()
		#state = guistate.level
		assert guistate.level == -1

	def logPoint(self):
		'utility method to trace control flow'
		callingFunction = inspect.stack()[1][3]
		currentTest = self.id().split('.')[-1]
		print 'in %s - %s()' % (currentTest, callingFunction)


if __name__ == '__main__':
	unittest.main()
