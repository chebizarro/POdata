"""
The classes contained in this module render an edmx document to a Dia Diagram
and back again.  

"""

# math is used for the Layer distribution algorythmn
import math

from collections import OrderedDict

import pyslet.odata2.csdl as edm
import pyslet.odata2.metadata as edmx
from pyslet.odata2.metadata import EntityType, EntityContainer, Property
from  pyslet.odata2.csdl import Association, AssociationEnd, NavigationProperty, EntitySet, AssociationSet, AssociationSetEnd, ComplexType

import dia

# for debugging only - disable for production!
from pudb import set_trace

class EdmxObjectMeta(type):
	"""
	The EdmxObjectMeta class creates a registry of Edmx classes and Dia types
	"""
	def __init__(cls, name, bases, dct):
		# we use __init__ rather than __new__ here because we want
		# to modify attributes of the class *after* they have been
		# created
		if not hasattr(cls, 'registry'):
			# this is the base class. Create an empty registry
			cls.registry = {}
		else:
			# this is a derived class. Add cls to the registry
			interface_id = name.lower()
			cls.registry[interface_id] = (cls, cls.DIATYPE, cls.EDMXTYPE)
		super(EdmxObjectMeta, cls).__init__(name, bases, dct)


class EdmxObjectFactory(object):
	"""
	The EdmxObjectFactory creates and returns Edmx Object instances
	"""
	@staticmethod
	def get_class_from_obj(obj) :
		"""
		Returns the Edmx class to use based on the passed Dia object
		@obj is a Dia object
		"""
		classes = []
		for cls, types in EdmxObject.registry.items():
			"""
			A Dia object may represent one of several Edmx classes, i.e.
			the UML-Class Dia Object is used to represent EntityType,
			EntityContainer and ComplexType 
			"""
			if obj.type.name == types[1] :
				classes.append(types)
		if len(classes) == 1 :
			"""
			See if there is only one Edmx class for this object type and
			return it,i.e. the UML - Association Dia object only represents
			the Edmx Association type
			"""
			return classes[0][0]
		for cls in classes :
			"""
			If there are multiple Edmx classes, look for the one that matches
			the Dia object's steretyope field
			"""
			# Using the globals function we can retrieve the Class using the
			# string value of the object's stereotype property
			if globals()[obj.properties.get("stereotype").value] == cls[2] :
				return cls[0]
		raise TypeError

	@staticmethod
	def get_class_from_entity(entity) :
		"""
		Return the Dia object class based on the passed Edmx entity
		@entity - the Edmx entity
		"""
		for cls, types in EdmxObject.registry.items() :
			if type(entity) == types[2] :
				return types[0]				
		raise TypeError

	@staticmethod
	def get_object(entity = None, obj = None, layer = None, diagram = None) :
		"""
		This is the main entry point to the Object Factory
		it returns a fully initialised instance of the Edmx class based
		on the passed parameters.
		@entity - the Edmx entity
		@obj - the Dia object
		@layer - the Edmx layer that the object is a part of
		@diagram - the Dia Diagram that the object is a part of  
		"""
		objtype = None

		if obj :
			# if the Dia object has been set we use it to determine the class
			try :
				objtype = EdmxObjectFactory.get_class_from_obj(obj)
			except TypeError:
				# should do something more useful and predictable?
				return None

		elif entity :
			# otherwise, if the entity has been set we use it to determine the class
			try :
				objtype = EdmxObjectFactory.get_class_from_entity(entity)
			except TypeError:
				# should do something more useful and predictable?
				return None
				
		# wrap the Dia object in a DiaObject wrapper
		diaobj = DiaObject(obj, objtype.DIATYPE)
		# create a new object based with the class name and parameters passed 
		newobj = objtype(layer.name, entity, diaobj, layer, diagram)
		if not obj :
			# if the Dia object was set, we call the update function
			#newobj.update()
			#else :
			# otherwise, we call create
			newobj.create()
		return newobj
			

class DiaObjectProperties(object) :
	def __init__(self, obj = None) :
		#if not self.items :
			#self.items = OrderedDict()
		# set defaults
		if obj :
			i = 0
			for key, value in self.items.items() :
				self.items[key] = obj[i]
				i += 1
	def __getattribute__(self, name) :
		items = object.__getattribute__(self, "items")
		try :
			return items[name]
		except AttributeError :
			return None	
		except KeyError:
			return object.__getattribute__(self, name)
	def __getitem__(self, key) :
		items = object.__getattribute__(self, "items")
		return items.values()[key]
	def __len__(self) :
		items = object.__getattribute__(self, "items")
		return len(items) 
	def __dir__(self):
		items = object.__getattribute__(self, "items")
		return items.keys() 
	def __setattr__(self, name, value) :
		items = object.__getattribute__(self, "items")
		items[name] = value
		
class DiaObjectAttr(DiaObjectProperties) :
	def __init__(self, obj = None) :
		items = OrderedDict((('name',None),('type' , None),('value' , None),('comment' , None),('visibility' , 0),('mumble' , 0),('scope', 0)))
		object.__setattr__(self, "items", items)
		super(DiaObjectAttr, self).__init__(obj)
		

class DiaObjectOps(DiaObjectProperties) :
	def __init__(self, obj = None) :
		items = OrderedDict((('name', None),('type',None),('comment',None),('stereotype',None),('visibility',None),('inheritance_type',None),('query',None),('class_scope',None),('params',None)))
		object.__setattr__(self, "items", items)
		super(DiaObjectOps, self).__init__(obj)
		
class DiaObjectOpsParams(DiaObjectProperties) :
	def __init__(self, obj = None) :
		items = OrderedDict((('name',None),('type',None),('value',None),('direction',None),('comment',None)))
		object.__setattr__(self, "items", items)
		super(DiaObjectOpsParams, self).__init__(obj)

class DiaObject(object):
	def __init__(self, obj, cls):
		'''
		@param obj: object to wrap
		'''
		object.__setattr__(self, "attributes", [])
		object.__setattr__(self, "operations", [])

		if obj :
			object.__setattr__(self, "obj", obj)
			"""
			attribs = []
			for item in obj.properties.get("attributes").value :
				attribs.append(DiaObjectAttr(*item))
			object.__setattr__(self, "attributes", attribs)
			ops = []
			for item in obj.properties.get("operations").value :
				ops.append(DiaObjectOps(*item))
			object.__setattr__(self, "operations", ops)
			"""
		else :
			oType = dia.get_object_type (cls)
			# we only need the object and not the handles
			diaobj = oType.create(0,0)[0] # p.x, p.y
			object.__setattr__(self, "obj", diaobj)
		
	def __getattribute__(self, name) :
		# get a reference to the Dia object
		obj = object.__getattribute__(self, "obj")
		if name == "diaobject" :
			return obj
		if name not in ("attributes", "operations") :
			# if the key is not one of the above special cases
			try :
				# first we check the properties of the dia object
				return obj.properties.get(name).value
			except AttributeError :
				return getattr(obj, name)
			except KeyError :
				# if there is non property by that name, check the object itself
				return getattr(obj, name)
		# if it is one of the special cases, we return that instead
		objitems = obj.properties.get(name).value
		selfitems = object.__getattribute__(self, name)
		if len(objitems) > len(selfitems) :
			if name == "attributes" :
				attrs = []
				for item in objitems :
					attrs.append(DiaObjectAttr(item))
				return attrs
			elif name == "operations" :
				attrs = []
				for item in objitems :
					attrs.append(DiaObjectOps(item))
				return attrs
		return selfitems

	def __setattr__(self, name, value) :
		obj = object.__getattribute__(self, "obj")
		if name not in ("attributes", "operations") :
			try :
				obj.properties[name] = value
			except KeyError :
				setattr(obj, name, value)
		else :
			values = []
			for field in value :
				values.append(tuple(field))
			obj.properties[name] = values
			object.__setattr__(self, name, value)
			
	def __dir__(self):
		obj = object.__getattribute__(self, "obj")
		return dir(obj)


	
"""
The EdmxObject is the base object for all Edmx diagram elements. It wraps both
and Edmx Element and a Dia Object and keeps them consistent
"""
class EdmxObject(object) :
	""" the Metaclass which sets up a dynamic type-mapping registry """
	__metaclass__ = EdmxObjectMeta
	""" The element's Dia type """
	DIATYPE = None
	""" The element's Edmx type """
	EDMXTYPE = None
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
	
	def create(self) :
		#if self.entity and not self.object.diaobject:
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
		self.object.name = self.name

	def set_type(self):
		"""
		Sets the class variable type
		This is entity specific
		The value is derived from the the xml entity's tag name
		"""
		self.type = self.entity.XMLNAME[1]

	def create_object(self) :
		"""
		This function creates a Dia Diagram Object from an xml entity
		This function should be over-riden in derived classes 
		"""
		pass

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

	def update_name(self) :
		"""
		Updates the object and entity's name to reflect the Dia Diagram object
		This should be over ridden for an Xml entity which defines its name differently 
		"""
		self.name = self.object.name
		self.entity.SetAttribute(('~','Name'),self.name)

	def update_type(self) :
		"""
		Updates the object's type to reflect that of the dia diagram obect's
		"""
		pass
		

class EdmxEntityType(EdmxObject) :
	DIATYPE = "UML - Class"
	EDMXTYPE = EntityType
	PROPTYPE = Property
	NAVTYPE = NavigationProperty
	
	def set_type(self) :
		super(EdmxEntityType, self).set_type()
		self.object.stereotype = self.type

	def create_object(self) :
		self._create_object_properties()
		self._create_object_nav_properties()
	
	def update(self) :
		super(EdmxEntityType, self).update()
		self._clear_keys()
		self._update_object_properties()
		self._update_object_nav_properties()
		self.entity.SetAttribute("Abstract", None)

	def update_type(self) :
		self.type = self.object.stereotype

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
			props = DiaObjectAttr()
			props.name = p.name
			props.type = p.type
			if not p.nullable :
				props.value = "NOT NULL"
			for key in self.entity.Key.PropertyRef :
				props.visibility = 2 if  p.name == key.name else 0
			attributes.append(props)
		self.object.attributes = attributes
		
	def _create_object_nav_properties(self) :
		"""
		Create the dia object's navigation properties (Operations) based on the xml entity
		"""
		methods = []
		# methods correspond to the NavigationProperty children of the xml entity
		for n in self.entity.NavigationProperty :
			props = DiaObjectOps()
			props.name = n.name
			methods.append(props)
		self.object.operations = methods

	def _update_object_properties(self):
		"""
		Update the xml entity's properties based on changes to the dia object
		"""
		objects = {}
		for prop in self.object.attributes :
			objects[prop.name] = prop
		for prop in self.entity.FindChildrenDepthFirst(self.PROPTYPE, False, 1) :
			try:
				self._update_property(prop, objects[prop.name])
				del objects[prop.name]
			except:
				self.entity.DeleteChild(prop)
		for prop in objects:
			self._update_property(self.entity.ChildElement(self.PROPTYPE),objects[prop])

	def _update_property(self, prop, value) :
		"""
		Update an xml entity's property based on changes to the dia object
		@prop = the xml property entity to be updated
		@value = a Property namedtuple wit the values from the dia object
		"""
		prop.SetAttribute("Name", value.name)
		prop.SetAttribute("Type", value.type)
		if value.value == "NOT NULL" :
			prop.SetAttribute("Nullable", "false")
		else :
			prop.SetAttribute("Nullable", None)
			
		if value.visibility == 2 :
			self._update_key(prop)

	def _update_object_nav_properties(self):
		"""
		Update an xml entity's navigation properties based on changes to the dia object
		"""
		ops = self.object.operations
		navobjects = {}
		for prop in ops :
			navobjects[prop.name] = prop
		for prop in self.entity.FindChildrenDepthFirst(self.NAVTYPE, False, 1) :
			try:
				newprops = navobjects[prop.name]
				self._update_nav_property(prop, newprops)
				del navobjects[prop.name]
			except:
				self.entity.DeleteChild(prop)
		indx = 8
		indx += len(self.object.attributes)*2
		for prop in navobjects:
			newnav = self.entity.ChildElement(self.NAVTYPE)
			newprops = DiaObjectOps(navobjects[prop])
			newnav.SetAttribute("Name", newprops.name)
			fromRole = toRole = ass = None
			role = [("b","a"),("a","b")]
			for i in range(0,2) :
				ass = self.object.connections[indx+i].connected
				if len(ass) > 0 :
					ass = DiaObject(ass[0],self.DIATYPE)
					fromRole = getattr(ass,"role_"+role[i][0])
					toRole = getattr(ass,"role_"+role[i][1])
					break
			if not ass:
				return
			newnav.SetAttribute("FromRole", fromRole)
			newnav.SetAttribute("ToRole", toRole)
			newnav.SetAttribute("Relationship", self.ns + "." + ass.name)
			indx +=2

	def _update_nav_property(self, prop, value) :
		prop.SetAttribute("Name", value.name)
		prop.SetAttribute("Association", value.stereotype)
		for param in value.params :
			end = prop.ChildElement(edm.AssociationSetEnd)
			end.Role = param[2]

	def _clear_keys(self) :
		try:
			for key in self.entity.Key.GetChildren() :
				self.entity.Key.DeleteChild(key)
		except AttributeError: pass

	def _update_key(self, key) :
		key_elem = self.entity.ChildElement(edm.Key)
		propRef = key_elem.ChildElement(edm.PropertyRef)
		propRef.name = key.name


class EdmxAssociation(EdmxObject) :
	"""
	Maps an Edmx Association entity to a Dia UML Association object
	"""
	DIATYPE = "UML - Association"
	EDMXTYPE = Association

	def __init__(self, ns, entity = None, obj = None, layer = None, diagram = None):
		self.layer = layer
		self.diagram = diagram
		super(EdmxAssociation, self).__init__(ns, entity, obj, layer, diagram)

	def create_object(self) :
		# There must always be 2 ends
		# todo:
		# - multiplicity
		# - error checking
		for role in ("a","b") :
			index = ord(role)-97
			end = self.entity.AssociationEnd[index]
			setattr(self.object, "role_" + role, end.name)
			setattr(self.object, "multipicity_" + role, edm.EncodeMultiplicity(end.otherEnd.multiplicity))
			obj = self.layer.objects[end.otherEnd.type]
			node = 8 + index
			node += len(obj.object.attributes)*2
			for prop in obj.entity.FindChildrenDepthFirst(edm.NavigationProperty, False, 1) :
				if prop.toRole == end.name :
					self.object.handles[index].connect(obj.object.connections[node])
					self.diagram.update_connections(self.object.diaobject)
					break
				node += 2

	def set_type(self):
		pass

	def update(self):
		self.update_name()
		self.update_object()

	def update_name(self) :
		self.name = self.object.name
		self.entity.SetAttribute(('~','Name'),self.name)

	def update_object(self) :
		try :
			self.entity.AssociationEnd[0].name = self.object.role_a
			self.entity.AssociationEnd[0].Multiplicity = self.object.multipicity_a
			self.entity.AssociationEnd[1].name = self.object.role_b
			self.entity.AssociationEnd[1].Multiplicity = self.object.multipicity_b
		except :
			for role in ("b", "a") :
				index = ord(role)-97
				end = self.entity.ChildElement(AssociationEnd,(self.entity.GetNS(),u"End"))
				end.name = getattr(self.object,"role_"+role)
				#this should return a DiaObject
				obj = self.object.handles[index].connected_to.object
				end.type = self.layer.name + "." + obj.properties.get("name").value
				end.multiplicity = edm.DecodeMultiplicity(getattr(self.object,"multipicity_"+role))
			
			
class EdmxEntityContainer(EdmxEntityType) :
	EDMXTYPE = EntityContainer
	PROPTYPE = EntitySet
	NAVTYPE = AssociationSet

	def create_object(self) :
		attributes = []
		methods = []
		for p in self.entity.EntitySet :
			props = DiaObjectAttr()
			props.name = p.name
			props.type = p.entityTypeName
			attributes.append(props)
		for n in self.entity.AssociationSet :
			params = DiaObjectOps()
			params.name = n.name
			params.type = n.associationName
			ends = []
			for end in n.AssociationSetEnd :
				attribs = DiaObjectOpsParams()
				attribs.name = end.name
				attribs.type = end.entitySet.name
				ends.append(tuple(attribs))
			params.params = ends
			methods.append(params)
		self.object.attributes = attributes
		self.object.operations = methods

	def update(self) :
		super(EdmxEntityType, self).update()
		self._update_object_properties()
		self._update_object_nav_properties()

	def _update_property(self, prop, value) :
		prop.SetAttribute("Name", value.name)
		prop.SetAttribute("EntityType", value.type)

	def _update_object_nav_properties(self):
		ops = self.object.operations
		navobjects = {}
		# iterate through all of the association sets
		for prop in ops :
			# we set a temporary list with each assiocation set properties
			navobjects[prop.name] = prop
		for prop in self.entity.FindChildrenDepthFirst(AssociationSet, False, 1) :
			# we iterate through the entity to update any existing children first
			try:
				newprops = DiaObjectOps(navobjects[prop.name])
				#self._update_nav_property(prop, newprops)
				# once we have updated the entity, we remove the assoc item from the temp list
				del navobjects[prop.name]
			except IndexError:
				# if it throws an IndexError exception, there is no corresponding object 
				self.entity.DeleteChild(prop)
		
		for prop in navobjects.values():
			# we iterate through the remaining association set objects and create them
			newprops = DiaObjectOps(navobjects[prop.name])
			newnav = self.entity.ChildElement(AssociationSet)
			newnav.SetAttribute("Name", newprops.name)
			newnav.SetAttribute("Association", newprops.type)
			for ends in newprops.params :
				end = DiaObjectOpsParams(ends)
				newend = newnav.ChildElement(AssociationSetEnd,(newnav.GetNS(),u"End"))
				newend.SetAttribute("Role",end.name)
				newend.SetAttribute("EntitySet",end.type)

	def _update_nav_property(self, prop, value) :
		prop.SetAttribute("Name", value.name)
		prop.SetAttribute("Association", value.stereotype)
		for end in prop.AssociationSetEnd :
			prop.DeleteChild(end)
		for param in value.params :
			end = DiaObjectOpsParams(param)
			newend = prop.ChildElement(AssociationSetEnd,(prop.GetNS(),u"End"))
			newend.SetAttribute("Role",end.name)
			newend.SetAttribute("EntitySet",end.type)

		
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
			if isinstance(entity, Association) :
				_deferred.append(entity)
			else :
				self.add_entity(entity)
		for entity in _deferred :
			self.add_entity(entity)

	def add_entity(self, entity) :
		# This function is a real choke point and needs to be reviewed
		obj = EdmxObjectFactory.get_object(entity, None,self, self.diagram)
		if obj :
			obj_name = self.layer.name + "." +  obj.name
			self.layer.add_object(obj.object.diaobject)
			self.objects[obj_name] = obj
		else :
			raise Exception

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
