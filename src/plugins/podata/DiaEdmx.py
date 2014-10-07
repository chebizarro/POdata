"""
The classes contained in this module render an edmx document to a Dia Diagram
and back again.  

"""

# math is used for the Layer distribution algorythmn
import math

import pyslet.odata2.csdl as edm
import pyslet.odata2.metadata as edmx
from pyslet.odata2.metadata import EntityType, EntityContainer, ComplexType
from  pyslet.odata2.csdl import Association, AssociationEnd

import sys
sys.path.append('/media/shared/projects/DiaPG/postdia/tests')

import dia

# for debugging only - disable for production!
from pudb import set_trace

from collections import namedtuple

""" EDMX Objects """
EdmxTypes = {
	"EntityContainer" : EdmxEntityContainer,
	"EntityType" : EdmxEntityType,
	"ComplexType": EdmxObject,
	"Association": EdmxAssociation
}

class EdmxObjectFactory(object):

	@staticmethod
	def get_class_from_obj(obj) :
		# see what class definitions exist for its DIATYPE
		classes = []
		for cls, types in DiaInterfaceMeta.registry.items()
			if obj.type == types[1] :
				classes.append(types)
		
		if len(classes) == 1 :
			# there is only edmx class for this object type
			return classes[0][0]
		
		for cls in classes :
			# if there are multiple, look for the one that matches
			# the object's steretyope field
			if obj.stereotype == cls[2] :
				return cls[0]
				
		raise TypeError

	@staticmethod
	def get_class_from_entity(entity) :
		# see what class definitions exist for its DIATYPE		
		for cls, types in DiaInterfaceMeta.registry.items()
			if entity.XMLNAME[1] == types[2] :
				return types[0]				
		raise TypeError

	@staticmethod
	def get_object(entity = None, obj = None, layer = None, diagram = None) :
		objtype = None
		if obj :
			try :
				objtype = EdmxObjectFactory.get_class_from_obj(obj)
			except TypeError:
				return None
		elif entity :
			try :
				objtype = EdmxObjectFactory.get_class_from_obj(entity)
		if objtype :
			newobj = objtype(layer.name, entity, obj, layer, diagram)
			newobj.create()
			return newobj
			
class DiaInterfaceMeta(type):
	# we use __init__ rather than __new__ here because we want
	# to modify attributes of the class *after* they have been
	# created
	# print(DiaInterfaceMeta.registry)
	def __init__(cls, name, bases, dct):
		if not hasattr(cls, 'registry'):
			# this is the base class.  Create an empty registry
			cls.registry = {}
		else:
			# this is a derived class.  Add cls to the registry
			interface_id = name.lower()
			cls.registry[interface_id] = (cls, cls.DIATYPE, cls.EDMXTYPE) 
			
		super(DiaInterfaceMeta, cls).__init__(name, bases, dct)


class DiaObjectProperties(object) :
	"""
	Abstract base class, not meant to be instantiated directly
	"""
	def __init__(self, obj):
		self.obj = obj
	def __getattribute__(self, name) :
		try :
			return obj.properties.get(self.type).value[self.properties.index(name)]
		except:
			raise AttributeError
	def __setattr__(self, name, value) :
		try :
			self.obj.properties[self.type][self.properties.index(name)] = value
		except:
			raise AttributeError

class DiaObjectAttributes(DiaObjectProperties) :
	self.type = "attributes"
	self.properties = ['name','type','value','comment','visibility','mumble','scope']

class DiaObjectOperations(DiaObjectProperties) :
	self.type = "operations"
	self.properties = ['name','type','comment','stereotype','visibility','inheritance_type','query','class_scope','params']
	
	def __init__(self, obj):
		super(DiaObjectOperations, self).__init(obj)
		self.params = []
	
	def __getattribute__(self, name) :
		try :
			if name != "params" :
				return obj.properties.get(self.type).value[self.properties.index(name)]
			return self.params
		except:
			raise AttributeError
	

class DiaObjectOperationsParams(DiaObjectProperties) :
	self.type = "operations"
	self.properties = ['name','type','value','direction','comment']
	def __getattribute__(self, name) :
		try :
			return obj.properties.get(self.type).value[8][self.properties.index(name)]
		except:
			raise AttributeError
	def __setattr__(self, name, value) :
		try :
			self.obj.properties[self.type][self.properties.index(name)][8] = value
		except:
			raise AttributeError


class DiaObject(object):
	def __init__(self, obj):
		'''
		@param obj: object to wrap
		'''
		self.obj = obj
		if obj.properties.get("attributes").value :
			self.properties["attributes"] = DiaObjectAttributes(obj)
		if obj.properties.get("operations").value :
			self.properties["operations"] = DiaObjectOperations(obj)

	def __getattribute__(self, name) :
		if name not in self.properties :
			try :
				return self.obj.properties[name]
			except:
				raise AttributeError
		return self.properties[name]
		
	def __setattr__(self, name, value) :
		if name not in self.properties :
			try :
				self.obj.properties[name] = value
			except:
				raise AttributeError

"""
The EdmxObject is the base object for all Edmx diagram elements. It wraps both
and Edmx Element and a Dia Object and keeps them consistent
"""
class EdmxObject(object) :
	__metaclass__ = DiaInterfaceMeta

	""" The element's Dia type """
	DIATYPE = "UML - Class"
	PROPERTY_TYPE = edmx.Property
	NAVPROPERTY_TYPE = edm.NavigationProperty
	"""
	different element types have different ways of representing their 
	name so we have to override and set it in each subclass as required
	"""
	def __init__(self, ns, entity = None, obj = None, *args):
		"""
		@ns = The Edmx xml entity's namespace, corresponds to the Dia layer name
		@entity = the Edmx xml entity
		@obj = the Dia Diagram Object
		@*args = some derived classes may need the additional layer and
			diagram parameters. The base class does not
		"""
		self.ns = ns
		self.entity = entity
		self.object = obj
		self.init_attributes()
		self.init_operations()
		

	
	def create(self) :
		if self.entity and not self.object:
			"""
			if we have an entity but no object, then we create the
			object based on the entity. This will generate a Dia object
			which will be added to the layer it is created in
			"""
			self.create_from_entity()
		"""
		Otherwise we leave it for the update() function to synchronise the
		Dia Diagram object with the xml entity
		"""
	
	def create_from_entity(self) :
		"""
		Create a Dia object from the provided Edmx xml entity
		It is not usually necessary to sublclass this method but depending
		on the entity type you may need to subclass set_name() and set_type() 
		"""
		oType = dia.get_object_type (self.DIATYPE)
		# we only need the object and not the handles
		self.object = oType.create(0,0)[0] # p.x, p.y
		self.set_name()
		self.set_type()
		self.create_object()
		"""	create_object should be over-riden in derived classes	"""

	def set_name(self):
		"""
		Sets the class variable name
		This is entity specific
		The name is derived from the xml entity's Name attribute
		This corresponds to the class name property in the Dia object
		"""
		self.name = self.entity.GetAttribute(('~','Name'))
		self.object.properties["name"] = self.name

	def set_type(self):
		"""
		Sets the class variable type
		This is entity specific
		The value is derived from the the xml entity's tag name
		This correspnds to the stereotype property in the Dia object
		"""
		self.type = self.entity.XMLNAME[1]
		self.object.properties["stereotype"] = self.type

	def create_object(self) :
		"""
		This function creates a Dia Diagram Object from an xml entity
		This function should be over-riden in derived classes 
		"""
		self._create_object_properties()
		self._create_object_nav_properties()

	def update(self) :
		"""
		The update function iterates through the EdmxObject's Dia Diagram object
		and synchronises it with the EdmxObjects xml entity, creating and removing
		elements as required. In case of conflicts, the Dia Diagram object's
		representation takes precedence
		This function should be over-riden in derived classes 
		"""
		self.update_name()
		self.update_type()
		self._update_object_properties()
		self._update_object_nav_properties()

	def update_name(self) :
		"""
		Updates the object and entity's name to reflect the Dia Diagram object
		This should be over ridden for an Xml entity which defines its name differently 
		"""
		self.name = self.object.properties.get("name").value
		self.entity.SetAttribute(('~','Name'),self.name)

	def update_type(self) :
		"""
		Updates the object's type to reflect that of the dia diagram obect's
		"""
		self.type = self.object.properties.get("stereotype").value
		
	"""
	Internal functions

	These functions keep the xml entity and Dia Diagram object synchronised
	They are modelled to work on the Basic Entity Type and should be over ridden
	in derived class where the entity's implementation requires 
	"""
	def _create_object_properties(self) :
		"""
		Create the dia object's properties (Attributes) based on the xml entity
		"""
		attributes = []
		# attributes correspond to the Property children of the xml entity
		for p in self.entity.Property :
			props = EdmxProperty(p.name)
			if not p.nullable :
				props.value = "NOT NULL"
			for key in self.entity.Key.PropertyRef :
				props.visibility = 2 if  p.name == key.name else 0
			attributes.append(props)
		self.object.properties["attributes"] = attributes
		
	def _create_object_nav_properties(self) :
		"""
		Create the dia object's navigation properties (Operations) based on the xml entity
		"""
		methods = []
		# methods correspond to the NavigationProperty children of the xml entity
		for n in self.entity.NavigationProperty :
			props = EdmxNavigationProperty(n.name)
			#params = []
			# params maps to the AssociationEnd elements in the xml entity 
			#params.append(("from","",n.fromRole,"",0))
			#params.append(("to","",n.toRole,"",0))
			methods.append(props)
		self.object.properties["operations"] = methods

	def _update_object_properties(self):
		"""
		Update the xml entity's properties based on changes to the dia object
		"""
		attribs = self.object.properties.get("attributes").value
		objects = {}
		for prop in attribs :
			objects[prop[0]] = prop
		for prop in self.entity.FindChildrenDepthFirst(self.PROPERTY_TYPE, False, 1) :
			try:
				self._update_property(prop, EdmxProperty(*objects[prop.name]))
				del objects[prop.name]
			except:
				self.entity.DeleteChild(prop)
		for prop in objects:
			self._update_property(
				self.entity.ChildElement(self.PROPERTY_TYPE),
				EdmxProperty(*objects[prop]))

	def _update_property(self, prop, value) :
		"""
		Update an xml entity's property based on changes to the dia object
		@prop = the xml property entity to be updated
		@value = a Property namedtuple wit the values from the dia object
		"""
		prop.SetAttribute("Name", value.name)
		prop.SetAttribute("Type", value.type)

	def _update_object_nav_properties(self):
		"""
		Update an xml entity's navigation properties based on changes to the dia object
		"""
		ops = self.object.properties.get("operations").value
		navobjects = {}
		for prop in ops :
			navobjects[prop[0]] = prop
		for prop in self.entity.FindChildrenDepthFirst(self.NAVPROPERTY_TYPE, False, 1) :
			try:
				newprops = EdmxNavigationProperty(*navobjects[prop.name])
				self._update_nav_property(prop, newprops)
				del navobjects[prop.name]
			except:
				self.entity.DeleteChild(prop)
		indx = 8
		indx += len(self.object.properties.get("attributes").value)*2
		for prop in navobjects:
			newnav = self.entity.ChildElement(self.NAVPROPERTY_TYPE)
			#newprops = NavigationProperty(*navobjects[prop])
			#newnav.SetAttribute("Name", newprops.name)
			#self._update_nav_property(newnav, indx)
			fromRole = toRole = ass = None
			role = [("b","a"),("a","b")]
			for i in range(0,1) :
				ass = self.object.connections[indx+i].connected
				if len(ass) > 0 :
					ass = ass[0]
					fromRole = ass.properties.get("role_"+role[i][0]).value
					toRole = ass.properties.get("role_"+role[i][1]).value
					break
			"""
			try :
				ass = self.object.connections[indx].connected
				ass = ass[0]
				fromRole = ass.properties.get("role_b").value
				toRole = ass.properties.get("role_a").value
			except:
				ass = self.object.connections[indx+1].connected
				ass = ass[0]
				fromRole = ass.properties.get("role_a").value
				toRole = ass.properties.get("role_b").value
			"""
			if not ass:
				return
			newnav.SetAttribute("FromRole", fromRole)
			newnav.SetAttribute("ToRole", toRole)
			newnav.SetAttribute("Relationship", self.ns + "." + ass.properties.get("name").value)
			indx +=2

class EdmxEntityType(EdmxObject) :
	def update(self) :
		self.update_name()
		self.update_type()
		self._clear_keys()
		self._update_object_properties()
		self._update_object_nav_properties()

	def _update_property(self, prop, value) :
		prop.SetAttribute("Name", value.name)
		prop.SetAttribute("Type", value.type)
		if value.value == "NOT NULL" :
			prop.SetAttribute("Nullable", "false")
		if value.visibility == 2 :
			self._update_key(prop)

	def _clear_keys(self) :
		try:
			for key in self.entity.Key.GetChildren() :
				self.entity.Key.DeleteChild(key)
		except KeyError: pass

	def _update_key(self, key) :
		key_elem = self.entity.ChildElement(edm.Key)
		propRef = key_elem.ChildElement(edm.PropertyRef)
		propRef.name = key.name


class EdmxAssociation(EdmxObject) :
	DIATYPE = "UML - Association"
	#layer = None
	def __init__(self, ns, entity = None, obj = None, layer = None, diagram = None):
		self.layer = layer
		self.diagram = diagram
		super(EdmxAssociation, self).__init__(ns, entity, obj, layer, diagram)

	def create_object(self) :
		self.object.properties["role_a"] = self.entity.AssociationEnd[0].name
		self.object.properties["multipicity_a"] = str(self.entity.AssociationEnd[0].multiplicity)
		self.object.properties["role_b"] = self.entity.AssociationEnd[1].name
		self.object.properties["multipicity_b"] = str(self.entity.AssociationEnd[1].multiplicity)
		idx = 0
		for end in self.entity.AssociationEnd :
			self._add_connector(end, self.object, idx)
			idx += 1

	def _add_connector(self, end, connector, index) :
		obj = self.layer.objects[end.otherEnd.type]
		node = 8 + index
		node += len(obj.object.properties.get("attributes").value)*2
		for prop in obj.entity.FindChildrenDepthFirst(self.NAVPROPERTY_TYPE, False, 1) :
			if prop.toRole == end.name :
				connector.handles[index].connect(obj.object.connections[node])
				self.diagram.update_connections(connector)
				break
			node += 2

	def set_type(self):
		pass

	def update(self):
		self.update_name()
		self._update_object_properties()

	def update_name(self) :
		self.name = self.object.properties.get("name").value
		self.entity.SetAttribute(('~','Name'),self.name)

	def _update_object_properties(self) :
		try :
			self.entity.AssociationEnd[0].name = self.object.properties.get("role_a").value
			self.entity.AssociationEnd[0].Multiplicity = self.object.properties.get("multipicity_a").value
			self.entity.AssociationEnd[1].name = self.object.properties.get("role_b").value
			self.entity.AssociationEnd[1].Multiplicity = self.object.properties.get("multipicity_b").value
		except :
			role_a = self.entity.GetElementClass((edm.EDM_NAMESPACE, 'End'))(self.entity)
			role_a.name = self.object.properties.get("role_a").value

			role_a_obj = self.object.handles[0].connected_to.object

			role_a.type = self.layer.name + "." + self.object.properties.get("name").value
			role_a.Multiplicity = self.object.properties.get("multipicity_a").value
			
			role_b = self.entity.ChildElement(AssociationEnd)
			role_b.name = self.object.properties.get("role_b").value
			role_b_obj = self.object.handles[1].connected_to.object
			role_b.type = self.layer.name + "." + role_b_obj.properties.get("name").value
			role_b.Multiplicity = self.object.properties.get("multipicity_b").value
			
			
class EdmxEntityContainer(EdmxObject) :
	PROPERTY_TYPE = edmx.EntitySet
	NAVPROPERTY_TYPE = edm.AssociationSet

	def create_object(self) :
		attributes = []
		methods = []
		for p in self.entity.EntitySet :
			props = EdmxProperty(p.name)
			props.type = p.xmlname
			attributes.append(props)
		for n in self.entity.AssociationSet :
			params = EdmxNavigationProperty(n.name)
			params.type = n.associationName
			methods.append(params)
		self.object.properties["attributes"] = attributes
		self.object.properties["operations"] = methods

	def _update_property(self, prop, value) :
		prop.SetAttribute("Name", value.name)
		prop.SetAttribute("EntityType", value.type)


	def _update_nav_property(self, prop, value) :
		prop.SetAttribute("Name", value.name)
		#prop.SetAttribute("Association", value.stereotype)
		for param in value.params :
			end = prop.ChildElement(edm.AssociationSetEnd)
			end.Role = param[2]
			#end.EntitySet = 

	def _update_object_nav_properties(self):
		ops = self.object.properties.get("operations").value
		navobjects = {}
		for prop in ops :
			navobjects[prop[0]] = prop
		for prop in self.entity.FindChildrenDepthFirst(self.NAVPROPERTY_TYPE, False, 1) :
			try:
				newprops = EdmxNavigationProperty(*navobjects[prop.name])
				self._update_nav_property(prop, newprops)
				del navobjects[prop.name]
			except:
				self.entity.DeleteChild(prop)



		
class EdmxLayer(object) :
	def __init__(self, layer, diagram, schema = None) :
		self.layer = layer
		self.name = layer.name
		self.diagram = diagram
		self.objects = {}
		self.schema = schema
		if schema :
			self.add_schema(schema)

	def add_schema(self, schema) :
		_deferred = []
		
		for entity in schema.GetChildren():
			
			if entity.XMLNAME[1] == "Association" :
				_deferred.append(entity)
			
			else :
				self.add_entity(entity)
		
		for entity in _deferred :
			self.add_entity(entity)

	def add_entity(self, entity) :
		# This function is a real choke point and needs to be reviewed
		obj = EdmxObjectFactory.get_object(entity,None,self, self.diagram)
		
		obj_name = self.layer.name + "." +  obj.name
		self.layer.add_object(obj.object)
		self.objects[obj_name] = obj

	def update(self) :
		for obj in self.layer.objects :
			objname = self.name + "." + obj.properties.get("name").value
			if not objname in self.objects :
				try :
					entity = self.schema.ChildElement(eval(obj.properties.get("stereotype").value))
				except :
					entity = self.schema.ChildElement(edm.Association)
				self.objects[objname] = EdmxObjectFactory.get_object(entity,obj,self, self.diagram)
			self.objects[objname].update()

	def distribute_objects(self) :
		width = 0.0
		height = 0.0
		for o in self.layer.objects :
			try:
				if width < o.properties["elem_width"].value :
					width = o.properties["elem_width"].value
				if height < o.properties["elem_height"].value : 
					height = o.properties["elem_height"].value
			except:
				pass
		# add 20 % 'distance'
		width *= 1.2
		height *= 1.2
		area = len (self.layer.objects) * width * height
		max_width = math.sqrt (area)
		x = 0.0
		y = 0.0
		dy = 0.0 # used to pack small objects more tightly
		for o in self.layer.objects :
			try :
				if dy + o.properties["elem_height"].value * 1.2 > height :
					x += width
					dy = 0.0
				if x > max_width :
					x = 0.0
					y += height
				o.move (x, y + dy)
				dy += (o.properties["elem_height"].value * 1.2)
				if dy > .75 * height :
					x += width
					dy = 0.0
				if x > max_width :
					x = 0.0
					y += height
				self.diagram.update_connections(o)
			except:
				pass


class DiaEdmx(object) :
	def __init__(self, name, diagramData = None, doc = None) :
		self.layers = {}
		self.name = name

		if not diagramData :
			self.diagram = dia.new(self.name + ".dia")
			self.data = self.diagram.data
			self.display = self.diagram.display()
		else :
			for diagram in dia.diagrams() :
				if diagram.data == diagramData :
					self.diagram = diagram
			self.data = diagramData
			try:
				self.display = self.diagram.displays[0]
			except:
				self.display = self.diagram.display()
		if doc:
			self.add_document(doc)
		else:
			self.doc = edmx.Document()
			root = self.doc.ChildElement(edmx.Edmx)
			dataservices = root.ChildElement(edmx.DataServices)
			version = dataservices.DataServiceVersion()
			if not version :
				dataservices.SetAttribute("DataServiceVersion","2.0")
		self.add_handlers()
		

	def add_document(self, document) :
		self.doc = document
		# blank the whole doc
		self.delete_layers()
		for schema in self.doc.root.DataServices.Schema:
			# can I do some funky with decorators or metaclass here?
			schemaName = schema.GetAttribute(('~','Namespace'))
			layer = self.data.add_layer(schemaName)
			self.new_layer(layer, schema)
	
	def update(self) :
		for layer in self.data.layers :
			self.update_layer(layer)
	
	def new_layer(self, layer, schema) :
		self.layers[layer.name]= EdmxLayer(layer, self.diagram, schema = schema)

	def delete_layers(self) :
		for layer in self.data.layers :
			if layer.name != "Background" :
				self.data.delete_layer(layer)
		self.layers = {}
				
	def update_layer(self, layer) :
		# We ignore the background layer
		if not layer.name in self.layers and layer.name != "Background" :
			# a hitherto unknown schema
			schema = self.doc.root.DataServices.ChildElement(edm.Schema)
			schema.SetAttribute(('~','Namespace'),layer.name)
			self.new_layer(layer, schema)
		try :
			self.layers[layer.name].update()
		except KeyError:
			pass

	def show(self) :
		prev_layer = None
		for layer in self.layers :
			self.layers[layer].distribute_objects()
			self.data.set_active_layer(self.layers[layer].layer)
		self.diagram.update_extents()
		self.diagram.flush()
		
	def save(self, filename = None) :
		self.update()
		if filename :
			f = open(filename, 'w')
			f.write(str(self.doc))
			f.close
		else :
			return str(self.doc)

	def add_handlers(self) :
		self.diagram.connect_after("removed", self.diagram_removed_cb)
		self.diagram.connect_after("selection_changed", self.diagram_sel_change_cb)
		self.data.connect_after("object_add", self.object_add_cb)
		self.data.connect_after("object_remove", self.object_remove_cb)

	def diagram_removed_cb(self, diagram) :
		print "Callback removed"

	def diagram_sel_change_cb(self, diagram, cb) :
		print "Callback sel changed"

	def object_add_cb(self, diagram, layer, evil) :
		print "Callback obj add"
		
	def object_remove_cb(self, diagram, layer, evil) :
		print "Callback obj remove"
