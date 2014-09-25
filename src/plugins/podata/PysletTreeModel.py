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
	def __init__(self, node, siblings = None, show_attribs = True) :
		self.node = node
		self.show_attribs = show_attribs
		self.previousSibling = None
		self.nextSibling = None
		
		if siblings :
			self.previousSibling = siblings[0]
			self.nextSibling = siblings[1]

	def next(self):
		if not self.nextSibling :
			result = self.node.nextSibling
			while self._is_blank_node(result) :
				result = result.nextSibling
			if result :
				self.nextSibling = XmlNodeIter(result, (self, None), self.show_attribs)
		return self.nextSibling
		
	def previous(self):
		if not self.previousSibling:
			result = self.node.previousSibling
			while self._is_blank_node(result) :
				result = result.previousSibling
			if result :
				self.previousSibling = XmlNodeIter(result, (None, self), self.show_attribs)
		if not self.previousSibling:
			if self.node.parentNode and self.show_attribs:
				if self.node.parentNode.attributes :
					idx = self.node.parentNode.attributes.length
					self.previousSibling = XmlAttrIter(self.node.parentNode, idx-1)
		return self.previousSibling
		
	def firstChild(self):
		if self.show_attribs and self.node.attributes  :
			return XmlAttrIter(self.node,0)
		if self.node.hasChildNodes() :
			child = self.node.firstChild
			while self._is_blank_node(child) :
				child = child.nextSibling
			if child :
				return XmlNodeIter(child, None, self.show_attribs)
		return None
		
	def parent(self):
		return XmlNodeIter(self.node.parentNode, None, self.show_attribs)
		
	def hasChildren(self):
		if self.show_attribs and self.node.attributes :
			return True
		if self.node.hasChildNodes() :
			for node in self.node.childNodes :
				if not self._is_blank_node(node) :
					return True
		return False
		
	def numChildren(self):
		num_nodes = 0
		if self.show_attribs and self.node.attributes :
			num_nodes += self.node.attributes.length
		if self.hasChildren() :
			for node in self.node.childNodes :
				if not self._is_blank_node(node) :
					num_nodes += 1
		return num_nodes
		
	def nthChild(self, n):
		idx = n
		if self.show_attribs :
			if n < self.node.attributes.length :
				return XmlAttrIter(self.node,n)
			else :
				idx = n-self.node.attributes.length
		node = self.firstChild().node
		for child in range(0, idx) :
			#result = node
			node = node.nextSibling
			while self._is_blank_node(node):
				node = node.nextSibling
		if node:
			return XmlNodeIter(node, None, self.show_attribs)
		return None
		
	def value(self, column):
		if column == 0:
			return self.node.nodeType
		elif column == 1:
			return self.node.prefix
		elif column == 2:
			if self.node.nodeType == Node.CDATA_SECTION_NODE :
				return "CDATA"
			if self.node.nodeType == Node.DOCUMENT_NODE :
				return "0"
			if self.node.nodeType == Node.TEXT_NODE :
				return "TEXT"
			if self.node.nodeType == Node.ATTRIBUTE_NODE :
				return self.node.name
			else :
				return self.node.tagName
		elif column == 3:
			if self.node.nodeType == Node.DOCUMENT_NODE or Node.ELEMENT_NODE:
				if self.node.hasChildNodes() :
					self.node.normalize()
					for child in self.node.childNodes :
						if child.nodeType == Node.TEXT_NODE :
							return child.data.strip()
						else :
							return None
			elif self.node.nodeType == Node.DOCUMENT_TYPE_NODE :
				return self.node.systemId
			elif self.node.nodeType == Node.TEXT_NODE :
				return self.node.data.strip()
			return self.node.nodeValue

	def isSameNode(self, node):
		if node :
			if self.node == node.node:
				return True
		return False
		
	def _is_blank_node(self, node) :
		value = None
		if node :
			if node.nodeType == Node.TEXT_NODE:
				if node.data :
					value = node.data.strip().strip("\n").strip("\p")
				if len(value) < 1 :
					return True
		return False

	@staticmethod
	def parse(xml):
		doc = None
		if isinstance(xml, str):
			try:
				doc = parseString(xml).documentElement
			except:
				doc = parse(xml).documentElement
		elif isinstance(xml, Node) :
			doc = xml.documentElement
		else:
			raise Exception("The object is not a valid XML object")
		return doc


class XmlAttrIter(XmlNodeIter) :
	def __init__(self, parent, index, siblings = None, show_attribs=True) :
		node = parent.attributes.item(index)
		if not node:
			return
		self.parentNode = parent
		self.index = index
		super(XmlAttrIter, self).__init__(node, siblings, show_attribs)

	def next(self):
		if not self.nextSibling :
			if(self.index < self.parentNode.attributes.length-1) :
				self.nextSibling =  XmlAttrIter(self.parentNode, self.index+1, (self, None), self.show_attribs )
			elif self.parentNode.hasChildNodes() :
				child = self.parentNode.firstChild
				while self._is_blank_node(child) :
					child = child.nextSibling
				if child :
					self.nextSibling = XmlNodeIter(child, (self, None))
		return self.nextSibling
	
	def previous(self):
		if not self.previousSibling :
			if(self.index > 0) :
				self.previousSibling = XmlAttrIter(self.parentNode, self.index-1, (None, self), self.show_attribs)
		return self.previousSibling

	def firstChild(self):
		return None

	def parent(self):
		return XmlNodeIter(self.parentNode, None, self.show_attribs)

	def hasChildren(self):
		return False

	def numChildren(self):
		return 0
		
	def nthChild(self, n):
		return None

class SETNodeIter(XmlNodeIter) :
	def __init__(self, node, siblings = None, show_attribs = True) :
		super(SETNodeIter, self).__init__(node, siblings, show_attribs)

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
							self.previousSibling = SETNodeIter(previous, (None, self), show_attribs)
						elif show_attribs :
							attribs = parent.GetAttributes()
							if attribs :
								
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
							self.nextSibling = SETNodeIter(nextNode, (self, None), show_attribs)
						break

	def next(self):
		return self.nextSibling
		
	def previous(self):
		return self.previousSibling
	
			
	def firstChild(self):
		if self.hasChildren() :
			try:
				firstchild = self.node.GetCanonicalChildren().next()
				return SETNodeIter(firstchild, None, self.show_attribs)
			except:
				pass
		return None
		
	def parent(self):
		if self.node.parent :
			return SETNodeIter(self.node.parent, None, self.show_attribs)
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
				return SETNodeIter(child, None, self.show_attribs)
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

	@staticmethod
	def parse(xml):
		doc = None
		if isinstance(xml, str):
			doc = edmx.Document()
			try:
				doc.Read(xml)
			except:
				with open(xml) as f:
					doc.Read(f)
		elif isinstance(xml, Node) :
			doc = xml
		else:
			raise Exception("The object is not a valid XML object")
		return doc.root
	


class XMLTreeModel(gtk.GenericTreeModel):

	column_types = (
		IntType,
		StringType,
		StringType,
		StringType
	)
	xml = None
	iter = None
	iter_class = XmlNodeIter
	
	def __init__(self, xml = None, iter_class = XmlNodeIter, update_xml = False, show_attribs = True):
		gtk.GenericTreeModel.__init__(self)
		self.set(xml, iter_class, update_xml, show_attribs)
		return
	"""
	Public set function
	"""
	def set(self, xml = None, iter_class = XmlNodeIter, update_xml = False, show_attribs = True) :
		if self.xml :
			if self.iter_class == XmlNodeIter :
				self.xml.unlink()
			self.invalidate_iters()
			self.xml = None
		self.iter_class = iter_class
		self.show_attribs = show_attribs
		if xml :
			try :
				self.xml = iter_class.parse(xml)
			except Exception as e:
				print e
				return

			self.iter = iter_class(self.xml)
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


