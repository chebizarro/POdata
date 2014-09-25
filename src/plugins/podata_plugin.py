#!/usr/bin/env python

#   Postgres SQL import export goodness
#   Copyright (C), 2014 Chris Daley <chebizarro@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# This module implements a Postgres SQL import and export dialog to connect
# to a Postgres SQL database server as well as an export module to dump a diagram
# to Postgres SQL compatible SQL.
#


# Make sure we use pygtk for gtk 2.0
import pygtk
pygtk.require("2.0")

import gtk

import pyslet.iso8601 as iso
import pyslet.odata2.csdl as edm
import pyslet.odata2.core as core
import pyslet.odata2.metadata as edmx

from podata.XmlTreeModel import XMLTreeModel
from podata import PysletTreeModel as PysletTreeModel


class Podata :
	
	windows = {}
	filename = None
	
	def __init__(self, standalone=True) :
		self.standalone = standalone
		gladefile = "podata/podata.glade"
		if not standalone :
			gladefile = "/usr/share/dia/python/" + gladefile 
		self.set_up_builder(gladefile)
		self.set_up_treeviews()
		self.open_window('main_window')
		self.set_up_chooser()
		self.set_up_statusbar()
		widget = dia.get_shell()
		widget.hide()
	
	# Handlers
	def on_main_window_destroy(self, widget, data=None) :
		#self.windows["main_window"].destroy()
		if self.standalone :
			gtk.main_quit()
		
	def on_toolbutton_open_clicked(self, widget, data=None) :
		self.doc = None
		self.filename = self.get_open_filename()
		if self.filename :
			doc = edmx.Document()
			with open(self.filename) as f:
				doc.Read(f)
			if isinstance(doc, edmx.Document):
				self.doc = doc
			elif isinstance(doc, edmx.Edmx):
				# create a document to hold the model
				self.doc = edmx.Document(root=doc)
			else:
				self.doc = self.filename
			ntype = type(self.doc)
			print ntype
			self.xml_view.get_model().get_model().set(self.doc, True)
			self.statusbar.push(self.context_id['open-file-status'], self.filename)

	def on_xml_view_row_activated(self, treeview, path, view_column) :
		treemodel = treeview.get_model().get_model()
		root = treeview.get_model().convert_path_to_child_path(path)
		attr_modelfilter = treemodel.filter_new(root=root)
		attr_modelfilter.set_visible_func(self.on_attr_tree_filter, data=None)
		self.attr_view.set_model(attr_modelfilter)

	def on_xml_tree_filter(self, model, iter, data) :
		n_type = model.get_value(iter,0)
		if n_type in (2,3):
			return False
		return True
		
	def on_attr_tree_filter(self, model, iter, data) :
		n_type = model.get_value(iter,0)
		if n_type == 2:
			return True
		return False
	
	# Utility functions
	
	def set_up_statusbar(self) :
		self.statusbar = self.builder.get_object("statusbar")
		self.context_id = {}
		self.context_id['open-file-status'] = self.statusbar.get_context_id('open-file-status')
	
	def set_up_builder(self, gladefile) :
		self.builder = gtk.Builder()
		self.builder.add_from_file(gladefile)
		self.builder.connect_signals(self)
	
	def set_up_chooser(self) :
		file_filter = gtk.FileFilter()
		file_filter.add_pattern("*.xml")
		file_filter.set_name("Metadata Files")
		self.chooser = gtk.FileChooserDialog(title="Choose a Metadata file",action=gtk.FILE_CHOOSER_ACTION_OPEN,parent = self.windows['main_window'],
			buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		self.chooser.set_filter(file_filter)
		
	def set_up_treeviews(self) :
		self.xml_view = self.builder.get_object("xml_view")
		self.attr_view = self.builder.get_object("attrib_view")
		treemodel = PysletTreeModel.XMLTreeModel()
		treemodelfilter = treemodel.filter_new(root=None)
		treemodelfilter.set_visible_func(self.on_xml_tree_filter, data=None)
		self.xml_view.set_model(treemodelfilter)
		
	def open_window(self, name) :
		if not (name in self.windows) :
			self.windows[name] = self.builder.get_object(name)
		self.windows[name].show_all()
		
	def get_open_filename(self) :	
		filename = None
		response = self.chooser.run()
		if response == gtk.RESPONSE_OK: filename = self.chooser.get_filename()
		self.chooser.hide()
		return filename

# set up as a dia plugin

try :
	import dia

	def open_podata_toolbar(data, flags) :
		Podata(False)

	dia.register_action("ToolbarPodataOpen","Open POdata",
		"/DisplayMenu/Dialogs/DialogsExtensionStart", open_podata_toolbar)

except :
	print 'Failed to import Dia ... running in Standalone mode'
	Podata(True)
	gtk.main()
