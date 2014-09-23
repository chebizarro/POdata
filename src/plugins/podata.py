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

import sys, math, types, string, re

# Make sure we use pygtk for gtk 2.0
import pygtk
pygtk.require("2.0")

import gtk

import podata

"""
import gtk.keysyms
import gtk.glade
import gobject
"""
"""
import pyslet.iso8601 as iso
import pyslet.odata2.csdl as edm
import pyslet.odata2.core as core
import pyslet.odata2.metadata as edmx




class ImportDbDialog :

	def export_sql(self, data) :
		export = DiaSql(dia.active_display().diagram.data)
		export.generateSQL()
		export.printSQL()
		self.quit(None, None)

	def set_fields(self) :
		self.dbname = self.dbEntry.get_text()
		self.user = self.userEntry.get_text()
		self.password = self.passwordEntry.get_text()
		self.host = self.serverEntry.get_text()
		self.port = self.serverPort.get_text()


	def import_cb(self, widget, data=None):
		self.set_fields()
		self.postgres_connect()
		
	def export_cb(self, widget, data=None):
		self.set_fields()
		self.export_sql(data)


class EdmxImporter :
	def __init__(self, sFile) :
		#load the file and verify it is an edmx
		doc = edmx.Document()
		with open(sFile) as f:
			doc.Read(f)
		if isinstance(doc, edmx.Document):
			self.doc = doc
		elif isinstance(doc, edmx.Edmx):
			# create a document to hold the model
			self.doc = edmx.Document(root=doc)
		else:
			raise TypeError("Edmx document or instance required for model")
        # update the base URI of the metadata document to identify this service

	def GetDefaultContainer(self, Schema) :
		#print type(Schema)
		for container in Schema.EntityContainer:
			if container.IsDefaultEntityContainer():
				return container
		

	def Parse(self) :
		container = self.GetDefaultContainer(self.doc.root.DataServices.Schema[0])
		self.diagram = DiaSchema(container.name)
		self.diagram.addEdmxContainer(container)	


	def Render(self) :
		self.diagram.show()
		return 0
		

def import_edmx(sFile, diagramData) :
	imp = EdmxImporter(sFile)
	imp.Parse()
	return imp.Render()
"""

class Podata :
	
	windows = {}
	filename = None
	
	def __init__(self, standalone=True) :
		if standalone == True :
			self.gladefile = "podata/podata.glade"
			self.builder = gtk.Builder()
			self.builder.add_from_file(self.gladefile)
			self.builder.connect_signals(self)
			self.set_up_treeview()
			self.open_window('main_window')
			self.filter = gtk.FileFilter()
			self.filter.add_pattern("*.xml")
			self.filter.set_name("Metadata Files")
			self.chooser = gtk.FileChooserDialog(title="Choose a Metadata file",action=gtk.FILE_CHOOSER_ACTION_OPEN,parent = self.windows['main_window'],
				buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
			self.chooser.set_filter(self.filter)
	
	# Handlers
	
	def on_main_window_destroy(self, widget, data=None) :
		for window in self.windows :
			if self.windows[window] :
				self.windows[window].destroy()
		gtk.main_quit()
		
	def on_toolbutton_open_clicked(self, widget, data=None) :
		self.filename = self.get_open_filename()
		if self.filename :
			self.xml_view.get_model().set(self.filename, True)

	def on_xml_view_row_activated(self, treeview, path, view_column) :
		model = treeview.get_model()
		
		pass
	# Utility functions
	
	def set_up_treeview(self) :
		self.xml_view = self.builder.get_object("xml_view")
		self.xml_view.set_model(podata.XmlTreeModel.XMLTreeModel())
		self.xml_view.append_column(self.add_column("Node",2))
		#self.xml_view.append_column(self.add_column("Content",3))
			

	def add_column(self, title, column_id) :
		column = gtk.TreeViewColumn(title, gtk.CellRendererText()
			, text=column_id)
		column.set_resizable(True)		
		column.set_sort_column_id(column_id)
		return column
		
		
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
	
	print "Podata Odata plugin loaded"
	
	def open_podata_toolbar(data, flags) :
		Podata(True)
		
	dia.register_action("ToolbarPodataOpen","Open Odata tools",
						"/DisplayMenu/Dialogs/DialogsExtensionStart",
						open_podata_toolbar)
	
	"""
	def open_dialog_import(data, flags):
		ImportDbDialog(data, "import")

	def open_dialog_export(data, flags):
		ImportDbDialog(data, "export")

	dia.register_action ("DialogsPostgresImp", "Import Postgres database", 
	                      "/DisplayMenu/Dialogs/DialogsExtensionStart", 
	                       open_dialog_import)

	dia.register_action ("DialogsPostgresExp", "Export diagram to Postgres", 
	                      "/DisplayMenu/Dialogs/DialogsExtensionStart", 
	                       open_dialog_export)
	                       
	dia.register_export ("Postgres SQL Export", "sql", SQLRenderer())
	
	dia.register_import("EDMX", "xml", import_edmx)
"""


except :
	print 'Failed to import Dia ... running in Standalone mode'
	Podata(True)
	gtk.main()
