from types import *
from xml.dom import Node
from xml.dom.minidom import parse, parseString, Attr 


import pyslet.iso8601 as iso
import pyslet.odata2.csdl as edm
import pyslet.odata2.core as core
import pyslet.odata2.metadata as edmx


import pygtk
pygtk.require("2.0")

import gtk

class XmlNodeIter(object) :
	def __init__(self, node, siblings = None) :
		self.node = node

		self.previousSibling = None
		self.nextSibling = None
		
		if siblings :
			self.previousSibling = siblings[0]
			self.nextSibling = siblings[1]

		
	def next(self):
		return self.nextSibling
		
	def previous(self):
		return self.previousSibling
		
	def firstChild(self):
		pass
		
	def parent(self):
		pass
		
	def hasChildren(self):
		pass
		
	def numChildren(self):
		pass
		
	def nthChild(self, n):
		pass
		
	def value(self):
		pass
		
	def isSameNode(self, node):
		if node :
			if self.node == node.node:
				return True
		return False

class SETNodeIter(XmlNodeIter) :
	def __init__(self, node, siblings = None) :
		super(SETNodeIter, self).__init__(node, siblings)

		if not self.previousSibling :
			if self.node.parent :
				parent = None
				previous = None
				try :
					parent = self.node.parent.GetCanonicalChildren()
				except:
					parent = self.node.parent.GetChildren()
				
				for sibling in parent :
					if sibling == self.node :
						if previous :
							self.previousSibling = SETNodeIter(previous, (None, self))
						break
					previous = sibling
		
		if not self.nextSibling :
			if self.node.parent :
				nextNode = None
				try :
					children = self.node.parent.GetCanonicalChildren()
				except :
					children = self.node.parent.GetChildren()
				for sibling in children :
					if sibling == self.node :
						try:
							nextNode = children.next()
						except:
							pass
						if nextNode :
							self.nextSibling = SETNodeIter(nextNode, (self, None))
						break
	
			
	def firstChild(self):
		if self.hasChildren() :
			try:
				firstchild = self.node.GetCanonicalChildren().next()
				return SETNodeIter(firstchild)
			except:
				pass
		return None
		
	def parent(self):
		if self.node.parent :
			return SETNodeIter(self.node.parent)
		return None
		
	def hasChildren(self):
		for child in self.node.GetCanonicalChildren() :
			return True
		return False
		
	def numChildren(self):
		numChildren = 0
		for child in self.node.GetCanonicalChildren() :
			numChildren += 1
		return numChildren
		
	def nthChild(self, n):
		numChildren = 0
		for child in self.node.GetCanonicalChildren() :
			if numChildren == n :
				return SETNodeIter(child)
		return None
		
	def value(self, column):
		if column == 0:
			#hmmmm
			return 1
		elif column == 1:
			return None
		elif column == 2:
			return self.node.GetXMLName()[1]
		elif column == 3:
			try:
				value = self.node.GetValue(True)
				return value
			except:
				return None
	


class XMLTreeModel(gtk.GenericTreeModel):

	column_types = (
		IntType,
		StringType,
		StringType,
		StringType
	)
	xml = None
	iter = None
	
	def __init__(self, xml = None, update_xml = False):
		gtk.GenericTreeModel.__init__(self)
		self.set(xml, update_xml)
		return
	"""
	Public set function
	"""
	def set(self, xml = None, update_xml = False) :
		if self.xml :
			#self.xml.unlink()
			self.invalidate_iters()
			self.xml = None
			
		if xml :
			if isinstance(xml, edmx.Document):
				self.xml = xml
			elif isinstance(xml, edmx.Edmx):
				# create a document to hold the model
				self.xml = edmx.Document(root=xml)
			elif type(xml) == str:
				doc = edmx.Document()
				try:
					doc.Read(xml)
				except:
					with open(xml) as f:
						doc.Read(f)
					#throw an error
					print "Error - lazy programmer"
				self.xml = doc

			if self.xml.root :
				self.xml = self.xml.root
				self.iter = SETNodeIter(self.xml)
				path = (0,)
				self.row_deleted(path)
				self.row_inserted(path, self.get_iter(path))
				self.row_has_child_toggled(path, self.get_iter(path))

	""" GenericTreeModel Interface handlers """
	"""
	The on_get_flags() method should return a value that is a combination of:
	gtk.TREE_MODEL_ITERS_PERSIST - TreeIters survive all signals emitted by the tree.
	gtk.TREE_MODEL_LIST_ONLY - The model is a list only, and never has children
	"""
	def on_get_flags(self) :
		""" our iterators contain a reference to the actual Node in the DOM so they persist """
		return gtk.TREE_MODEL_ITERS_PERSIST
	"""
	The on_get_n_columns() method should return the number of columns that your model exports
	to the application.		
	"""
	def on_get_n_columns(self) :
		return len(self.column_types)
	"""
	The on_get_column_type() method should return the type of the column with the specified index.
	This method is usually called from a TreeView when its model is set.
	"""
	def on_get_column_type(self, index) :
		if index >= len(self.column_types) or index < 0:
			return None
		return self.column_types[index]
	"""
	The on_get_iter() method should return an rowref for the tree path specified by path.
	The tree path will always be represented using a tuple. 
	"""
	def on_get_iter(self, path) :
		if not self.iter : return None
		tree = self.iter
		result = self.iter
		for pos in path :
			result = tree
			for num in range(0,pos) :
				tree = tree.next()
			result = tree
			if tree :
				tree = tree.firstChild()
		if result :
			return self.create_tree_iter(result)
		return None
	"""
	The on_get_path() method should return a tree path given a valid rowref
	"""
	def on_get_path(self, iter) :
		if not iter :
			return None
		if not self.iter_is_valid(iter) :
			return (0,)
		iter_data = self.get_user_data(iter)
		tree = self.iter
		path = ()
		idx = 0
		while not tree.isSameNode(iter_data) and iter_data :
			prev = iter_data.previous()
			if not prev :
				path = (idx,) + path
				iter_data = iter_data.parent()
				idx = 0
			else :
				iter_data = prev
				idx += 1
		path = (0,) + path
		return path
	"""
	The on_get_value() method should return the data stored at the row and column specified by iter and column. 
	XML_TREE_MODEL_COL_TYPE = 0,
	XML_TREE_MODEL_COL_NS,
	XML_TREE_MODEL_COL_NAME,
	XML_TREE_MODEL_COL_CONTENT,
	"""	
	def on_get_value(self, iter, column) :
		if iter :
			if self.iter_is_valid(iter) :
				iter_data = self.get_user_data(iter)
				if iter_data :
					return iter_data.value(column)
		return None

	"""
	The on_iter_next() method should return a TreeIter to the row (at the same level) after the row specified by iter
	or None if there is no next row
	"""
	def on_iter_next(self, iter) :
		if self.iter_is_valid(iter) :
			iter_data = self.get_user_data(iter)
			record = iter_data.next()
			if record :
				return self.create_tree_iter(record)
		return None
	"""
	The on_iter_children() method should return a row reference to the first child row
	of the row specified by parent. If parent is None, a reference to the first top level
	row is returned. If there is no child row None is returned.
	"""
	def on_iter_children(self, parent) :
		child = self.iter
		if self.iter_is_valid(parent) :
			iter_data = self.get_user_data(parent)
			child = iter_data.firstChild()
			if not child :
				return None
		return self.create_tree_iter(child)
	"""
	The on_iter_has_child() method should return TRUE if the row specified by iter
	has child rows; FALSE otherwise. Our example returns FALSE since no row can have a child:
	"""
	def on_iter_has_child(self, iter) :
		if iter :
			if self.iter_is_valid(iter) :
				iter_data = self.get_user_data(iter)
				return iter_data.hasChildren()
		return False
	"""
	The on_iter_n_children() method should return the number of child rows that the row specified by
	iter has. If iter is None, the number of top level rows is returned.
	"""
	def on_iter_n_children(self, iter) :
		if iter:
			if self.iter_is_valid(iter) :
				iter_data = self.get_user_data(iter)
				return iter_data.numChildren()
		return 1
	"""
	The on_iter_nth_child() method should return a row reference to the nth child row of the row
	specified by parent. If parent is None, a reference to the nth top level row is returned.
	"""
	def on_iter_nth_child(self, parent, n) :
		node = None 
		if parent :
			if self.iter_is_valid(parent) :
				parent = self.get_user_data(parent)
			if parent.numChildren() > n :
				node = parent.nthChild(n)
		else :
			if n == 0 :
				node = self.iter
		if node:
			return self.create_tree_iter(node)			
		return None
		
	"""
	The on_iter_parent() method should return a row reference to the parent row of the row specified by child.
	If rowref points to a top level row, None should be returned.
	"""
	def on_iter_parent(self, child) :
		if child :
			if self.iter_is_valid(child) :
				iter_data = self.get_user_data(child)
				if not iter_data.isSameNode(self.iter) :
					parent = iter_data.parent()
					return self.create_tree_iter(parent)
		return None


