from types import *
from xml.dom import Node
from xml.dom.minidom import parse, parseString, NamedNodeMap, getDOMImplementation

import pygtk
pygtk.require("2.0")

import gtk

class XMLTreeModel(gtk.GenericTreeModel):

	column_types = (
		IntType,
		StringType,
		StringType,
		StringType
	)
	xml = None
	
	def __init__(self, xml_file = None, update_xml = False):
		gtk.GenericTreeModel.__init__(self)
		self.set(xml_file, update_xml)
		return
	"""
	Public set function
	"""
	def set(self, xml_file = None, update_xml = False) :
		if self.xml :
			self.xml.unlink()
			self.invalidate_iters()
			self.xml = None
		if type(xml_file) == Node:
			self.xml = xml_file
		elif type(xml_file) == str:
			try:
				self.xml = parse(xml_file)
			except:
				try:
					self.xml = parseString(xml_file)
				except:
					print("Invalid file " + xml_file)
					self.xml = None
		if self.xml :
			self.xml = self.xml.documentElement
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
		if not self.xml : return None
		tree = self.xml
		result = self.xml
		for pos in path :
			result = tree
			for num in range(0,pos) :
				tree = self._next_element_sibling(tree)
			result = tree
			tree = self._first_element_child(tree)
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
		tree = self.xml
		path = ()
		idx = 0
		while not tree.isSameNode(iter_data) and iter_data :
			prev = self._previous_element_sibling(iter_data)
			if not prev :
				path = (idx,) + path
				iter_data = iter_data.parentNode
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
		if not iter :
			return None
		if not self.iter_is_valid(iter) :
			return None
		iter_data = self.get_user_data(iter)
		if not iter_data:
			return None
		if column == 0:
			return iter_data.nodeType
		elif column == 1:
			return iter_data.prefix
		elif column == 2:
			if iter_data.nodeType == Node.CDATA_SECTION_NODE :
				return "CDATA"
			if iter_data.nodeType == Node.DOCUMENT_NODE :
				return "0"
			if iter_data.nodeType == Node.TEXT_NODE :
				return "TEXT"
			else :
				return iter_data.tagName
		elif column == 3:
			return self._get_node_content(iter_data)
	"""
	The on_iter_next() method should return a TreeIter to the row (at the same level) after the row specified by iter
	or None if there is no next row
	"""
	def on_iter_next(self, iter) :
		if self.iter_is_valid(iter) :
			iter_data = self.get_user_data(iter)
			record = self._next_element_sibling(iter_data)
			if record :
				return self.create_tree_iter(record)
		return None
	"""
	The on_iter_children() method should return a row reference to the first child row
	of the row specified by parent. If parent is None, a reference to the first top level
	row is returned. If there is no child row None is returned.
	"""
	def on_iter_children(self, parent) :
		child = self.xml
		if self.iter_is_valid(parent) :
			iter_data = self.get_user_data(parent)
			child = self._first_element_child(iter_data)
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
				return self._has_child_nodes(iter_data)
		return False
	"""
	The on_iter_n_children() method should return the number of child rows that the row specified by
	iter has. If iter is None, the number of top level rows is returned.
	"""
	def on_iter_n_children(self, iter) :
		if iter:
			if self.iter_is_valid(iter) :
				iter_data = self.get_user_data(iter)
				return self._n_child_nodes(iter_data)
		return 1
	"""
	The on_iter_nth_child() method should return a row reference to the nth child row of the row
	specified by parent. If parent is None, a reference to the nth top level row is returned.
	"""
	def on_iter_nth_child(self, parent, n) :
		node = self.xml
		if parent :
			if self.iter_is_valid(parent) :
				node = self.get_user_data(parent)
			if self._n_child_nodes(node) >= n :
				node = self._get_n_child(node, n)
		elif n > 1 :
			return None
		if node :
			return self.create_tree_iter(node)
	"""
	The on_iter_parent() method should return a row reference to the parent row of the row specified by child.
	If rowref points to a top level row, None should be returned.
	"""
	def on_iter_parent(self, child) :
		if child :
			if self.iter_is_valid(child) :
				iter_data = self.get_user_data(child)
				if not iter_data.isSameNode(self.xml) :
					parent = iter_data.parentNode
					return self.create_tree_iter(parent)
		return None
	"""
	
	Internal functions
	
	"""
	def _first_element_child(self, node) :
		if node :
			if node.hasChildNodes :
				node = node.firstChild
				while self._is_blank_node(node) :
					node = node.nextSibling
				if node :
					return node
		return None

	def _next_element_sibling(self, node) :
		if not node:
			return None
		record = node.nextSibling
		#if node.nodeType == Node.ATTRIBUTE_NODE :
		#	if not record :
		#		record = node.parentNode.firstChild
		while self._is_blank_node(record) :
			record = record.nextSibling
		return record

	def _previous_element_sibling(self, node) :
		if not node:
			return None
		record = None
		if node.nodeType == Node.ELEMENT_NODE :
			record = node.previousSibling
			while self._is_blank_node(record) :
				record = record.previousSibling
			#if not record :
			#	record = node.parentNode.attributes
			#	if record :
			#		while record.nextSibling :
			#			record = record.nextSibling
		elif node.nodeType == Node.TEXT_NODE :
			while self._is_blank_node(record) :
				record = record.previousSibling
		#elif node.nodeType == Node.ATTRIBUTE_NODE :
		#	record = node.parentNode.firstChild
		elif node.nodeType == Node.DOCUMENT_NODE :
			record = None
		return record

	def _is_blank_node(self, node) :
		value = None
		if node :
			if node.nodeType == Node.TEXT_NODE:
				value = node.data.strip().strip("\n").strip("\p")
				if len(value) < 1 :
					return True
		return False

	def _get_node_content(self, node) :
		if node.nodeType == Node.DOCUMENT_NODE or Node.ELEMENT_NODE:
			if node.hasChildNodes() :
				node = self._first_element_child(node)
				if node:
					if node.nodeType == Node.TEXT_NODE :
						return node.data.strip()
				return None
		elif node.nodeType == Node.DOCUMENT_TYPE_NODE :
			return node.systemId
		return node.nodeValue

	def _has_child_nodes(self, parent) :
		if parent.hasChildNodes() :
			for node in parent.childNodes :
				if not self._is_blank_node(node) :
					return True
		return False

	def _n_child_nodes(self, parent) :
		num_nodes = 0
		if self._has_child_nodes(parent) :
			for node in parent.childNodes :
				if not self._is_blank_node(node) :
					num_nodes += 1
		return num_nodes

	def _get_n_child(self, parent, n) :
		children = []
		for node in parent.childNodes :
			if not self._is_blank_node(node) :
				children.append(node)
		if len(children) > n :
			return children[n]
		return None
		
