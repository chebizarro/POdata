

class DiaEdmx :
	
	def __init__(self, name) :
		self.name = name
		self.diagram = dia.new(self.name + ".dia")
		self.data = self.diagram.data
		display = self.diagram.display()

	def addDocument(self, document) :
		self.doc = document
		for schema in self.doc.root.DataServices.Schema:
			self.addLayer(schema)


	def addLayer(self, schema) :
		
		layer = self.data.add_layer(schema.Namespace)
		
		for container in schema.EntityContainer :
			self.addEntity(container, layer)

		for entity in schema.EntityType :
			self.addEntity(entity, layer)
		
		for complexType in schema.ComplexType :
			self.addEntity(complexType, layer)

		for assoc in schema.Association :
			self.addAssociation(assoc, layer)
			
			

	def addEntity(self, entity, layer) :
		oType = dia.get_object_type ("UML - Class")
		o, h1, h2 = oType.create (0,0) # p.x, p.y
		o.properties["name"] = entity.name
		o.properties["stereotype"] = entity.type

		attributes = []
		methods = []
		
		if entity.type == "EntityContainer" :
		
			for p in entity.EntitySet :
				name = p.name
				visibility = 0
				atype = p.entityType
				# (name, type, value, comment, kind)
				attributes.append((name, atype, "","",visibility,0,0))

			for n in entity.AssociationSet :
				params = []
				for r in n.End :
					params.append((r.role, r.entitySet,n.fromRole,"",0))
				# (name, type, comment, stereotype, visibility, inheritance_type, query,class_scope, params)
				methods.append((n.name, n.type,"",n.association,0,0,0,0,params))
		
		else :
			
			for p in entity.Property :
				name = p.name
				default = ""
				value = ""
				null = "NULL"
				visibility = 0
				atype = p.type
				if p.nullable == False:
					null = "NOT NULL"
								
				if p.name == entity.Key.PropertyRef[0].name :
					visibility = 2
				
				value += null
				# (name, type, value, comment, kind)
				attributes.append((name, atype, value,"",visibility,0,0))

			for n in entity.NavigationProperty :
				params = []
				params.append(("from","",n.fromRole,"",0))
				params.append(("to","",n.toRole,"",0))
				# (name, type, comment, stereotype, visibility, inheritance_type, query,class_scope, params)
				methods.append((n.name, "","","",0,0,0,0,params))
			
		o.properties["attributes"] = attributes
		o.properties["operations"] = methods
		layer.add_object(o)
		self.objects[entity.name] = o
		

	def addAssociation(self, association, layer) :
		start_node = 8
		finish_node = 9
		oType = dia.get_object_type ("UML - Association")
		o, h1, h2 = oType.create(0,0)
		idx = 0
		
		for idx in range(0,1) :
			end = association.End[idx]
			self.addConnector(end, o, idx)
			idx += 1

		self.layer.add_object (o)


	def addConnector(self, end, connector, index) :
		obj = self.objects[end.type.name]

		node = 8 + index
		node += (len(obj.properties)*2)

		for prop in obj.properties.get("operations").value :
			if prop[0] == end.type.name :
				connector.handles[index].connect(obj.connections[node])
				self.diagram.update_connections(connector)
				break
			node += 2
		

	def show(self) :
		self.distribute_objects ()
		if self.diagram :
			self.diagram.update_extents()
			self.diagram.flush()

	def distribute_objects (self) :
		for layer in self.data.layers :
			width = 0.0
			height = 0.0
			for o in layer.objects :			
				if str(o.type) != "UML - Constraint" :
					if width < o.properties["elem_width"].value :
						width = o.properties["elem_width"].value
					if height < o.properties["elem_height"].value : 
						height = o.properties["elem_height"].value
			# add 20 % 'distance'
			width *= 1.2
			height *= 1.2
			area = len (layer.objects) * width * height
			max_width = math.sqrt (area)
			x = 0.0
			y = 0.0
			dy = 0.0 # used to pack small objects more tightly
			for o in layer.objects :
				if str(o.type) != "UML - Constraint" :
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

