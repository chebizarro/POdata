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

import sys
#sys.path.append('../../tests/dia')


import gtk

import pyslet.iso8601 as iso
import pyslet.odata2.csdl as edm
import pyslet.odata2.core as core
import pyslet.odata2.metadata as edmx

from podata import PysletTreeModel
from podata import DiaEdmx

class Podata :
	windows = {}
	diagrams = {}
	filename = None
	gladefile = "/media/shared/projects/DiaPG/postdia/src/plugins/podata/podata.glade"
	export_file = None
	
	def __init__(self, standalone=True) :
		self.standalone = standalone
		self.set_up_builder(self.gladefile)
		self.set_up_treeviews()
		self.set_up_mainwindow()
		self.set_up_chooser()
		self.set_up_statusbar()
	
	# UI Handlers
	def on_main_window_destroy(self, widget, data=None) :
		widget.hide_all()
		if self.standalone :
			self.quit()

	def on_main_window_delete_event(self,widget, data=None) :
		widget.hide_all()
		if self.standalone :
			self.quit()
		
	def on_toolbutton_open_clicked(self, widget, data=None) :
		self.doc = None
		self.filename = self.get_open_filename()
		if self.filename :
			self.xml_view.get_model().get_model().set(self.filename, PysletTreeModel.SETNodeIter, True, True)
			self.statusbar.push(self.context_id['open-file-status'], self.filename)

	def on_xml_view_row_activated(self, treeview, path, view_column) :
		treemodel = treeview.get_model().get_model()
		root = treeview.get_model().convert_path_to_child_path(path)
		root_iter = treemodel.get_iter(root)
		value = treemodel.get_value(root_iter,2)
		if value == "Schema" :
			node = treemodel.get_value(root_iter,4)
			self.open_diagram_from_doc(self.filename.split(".")[0], node.node.GetDocument())
		#attr_modelfilter = treemodel.filter_new(root=root)
		#attr_modelfilter.set_visible_func(self.on_attr_tree_filter, data=None)
		#self.attr_view.set_model(attr_modelfilter)

	def on_xml_tree_filter(self, model, iter, data) :
		n_type = model.get_value(iter,0)
		if n_type in (2,3):
			pass
			#return False
		return True
		
	def on_attr_tree_filter(self, model, iter, data) :
		n_type = model.get_value(iter,0)
		if n_type == 2:
			return True
		return False
	
	# UI Utility functions

	def set_up_mainwindow(self) :
		self.windows['main_window'] = self.builder.get_object('main_window')
	
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

	def run(self) :
		gtk.main()
		
	def quit(self):
		gtk.main_quit()
		return False


	# General plugin functions

	def open_diagram_from_doc(self, name, doc) :
		self.diagrams[name] = DiaEdmx.DiaEdmx(name)
		self.diagrams[name].addDocument(doc)
		self.diagrams[name].show()

	def import_edmx(self, sFile, diagramData) :
		doc = edmx.Document()
		try:
			with open(sFile) as f:
				doc.Read(f)
		except:
			raise TypeError("Must be an Edmx document")
		name = sFile
		self.diagrams[name] = DiaEdmx.DiaEdmx(name, diagramData)
		self.diagrams[name].addDocument(doc)
		self.diagrams[name].show()
		return self.diagrams[name]

	def begin_render (self, data, filename) :
		export = None
		for diagram in self.diagrams :
			if self.diagrams[diagram].data == data :
				self.diagrams[diagram].update()
				export = self.diagrams[diagram]
		if not export :
			name = filename
			export = DiaEdmx.DiaEdmx(name, data)
		export.update()
		self.export_file = open(filename, "w")
		self.export_file.write(str(export.doc))

	def end_render (self) :
		self.export_file.close()
		self.export_file = None
		pass

def open_podata_toolbar(data, flags) :
	global app
	if not app :
		app = Podata(standalone)
	else :
		app.open_window("main_window")


def main(standalone = True):
	global app # hook for tests
	app = Podata(standalone)
	if standalone :
		app.run()
		#app.open_window("main_window")
	else :
		dia.register_action("ToolbarPodataOpen","Open POdata",
			"/DisplayMenu/Dialogs/DialogsExtensionStart", open_podata_toolbar)
							   
		dia.register_export ("EDMX", "xml", app)
		
		dia.register_import("EDMX", "xml", app.import_edmx)


# set up as a dia plugin
try :
	import dia
	main(False)

except Exception as e :
	#import dia
	#print e
	print 'Failed to import Dia'


if __name__ == '__main__':
    main(True)
