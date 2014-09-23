
class SQLRenderer :
	def __init__ (self) :
		pass
		
	def begin_render (self, data, filename) :
		self.f = open(filename, "w")
		self.sql = DiaSql(data)
		self.sql.generateSQL()
		self.f.write(self.sql.SQL)

	def end_render (self) :
		self.f.close()


class DiaSql :
	
	reserved = ["all","analyse","analyze","and","any","array","as","asc","asymmetric","both","case","cast","check","collate","column","constraint","create","current_catalog","current_date","current_role","current_time","current_timestamp","current_user","default","deferrable","desc","distinct","do","else","end","except","false","fetch","for","foreign","from","grant","group","having","in","initially","intersect","into","lateral","leading","limit","localtime","localtimestamp","not","null","offset","on","only","or","order","placing","primary","references","returning","select","session_user","some","symmetric","table","then","to","trailing","true","union","unique","user","using","variadic","when","where","window","with","authorization","binary","collation","concurrently","cross","current_schema","freeze","full","ilike","inner","is","isnull","join","left","like","natural","notnull","outer","over","overlaps","right","similar","verbose"]
	
	def __init__(self, data) :
		self.data = data
		self.layer = data.active_layer
		self.SQL = "--\n-- PostgreSQL database dump\n--\n-- Created by postdia PostgreSQL plugin\n--\n-- https://github.com/chebizarro/postdia\n--\n\n"
		self.SQL += "CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;\n\n"

	def generateSQL(self) :
		TSQL = ""
		SSQL = ""
		CSQL = ""
		CMSQL = ""
		
		for obj in self.layer.objects :
			if str(obj.type) == "UML - Class" :
				TSQL += self.generateTable(obj)
			elif str(obj.type) == "UML - SmallPackage" :
				SSQL += self.generateSequence(obj)
			elif str(obj.type) == "UML - Constraint" :
				CSQL += self.generateConstraint(obj)
			elif str(obj.type) == "UML - Component" :
				CMSQL += self.generateData(obj) 
				
		self.SQL += SSQL + TSQL + CSQL + CMSQL

	def generateTable(self, obj) :
		noprops = len(obj.properties.get("attributes").value)
		idx = 1
		pattern = r"'(.*?)'"
		seq = ""
		seqCol = ""
		tableName = obj.properties.get("name").value

		if tableName in self.reserved :
			tableName = '"' + tableName + '"'
			
		sql = "CREATE TABLE " + tableName + " (\n"

		for att in obj.properties.get("attributes").value :
			#(name,type,value,comment,visibility,abstract,class_scope)
			quotes = ""
			if att[4] == 2 :
				m = re.search(pattern, att[2])
				if m != None :
					seq = m.group()
					seqCol += "ALTER SEQUENCE " + seq.strip("'") + " OWNED BY " + tableName + "." + att[0] + ";\n\n"

			if att[0] in self.reserved :
				quotes = '"'
			sql += "\t" + quotes + att[0] + quotes + " " + att[1] + " " + att[2]
			if idx < noprops:
				sql += ","
			sql += "\n"
			idx += 1
		sql += ");\n\n"
		
		sql += seqCol
		
		# create indices
		# (name, type, comment, stereotype, visibility, inheritance_type, query,class_scope, params)
		for op in obj.properties.get("operations").value :
			if op[1] == "primary key" :
				sql += "ALTER TABLE ONLY " + tableName + "\n ADD CONSTRAINT " + op[0] + " PRIMARY KEY (" + op[8][0][0] + ");\n\n"
			else :		
				sql += "CREATE "
				if op[1] == "unique index" :
					sql += "UNIQUE "
				sql += "INDEX " + op[0] + " ON " + tableName + " USING btree (" + op[8][0][0] + ");\n\n" 
		
		return sql
		
	def generateSequence(self, obj) :
		return "\n" + str(obj.properties["text"].value.text) + "\n\n"
		
	def generateConstraint(self, obj) :
		t1 = obj.handles[0].connected_to.object
		t2 = obj.handles[1].connected_to.object
		idxname = self.getConnectedField(obj, t1, 0)
		tgtname = self.getConnectedField(obj, t2, 1)
		sql = "ALTER TABLE ONLY " + t1.properties.get("name").value + "\n"
		sql += "\tADD CONSTRAINT " + obj.properties.get("constraint").value + " FOREIGN KEY ("
		sql += idxname + ") REFERENCES " + t2.properties.get("name").value +"(" + tgtname + ") ON UPDATE SET NULL ON DELETE SET NULL DEFERRABLE;\n\n"
		return sql
	
	def getConnectedField(self, obj1, obj2, handle) :
		cnt = 0
		for i in obj2.connections :
			if i == obj1.handles[handle].connected_to :
				break
			cnt+=1
		idx = 0
		idxname = ""	
		for att in obj2.properties.get("attributes").value :
			if idx == ((cnt-8)/2) :
				idxname = att[0]
				break
			idx += 1		
		return idxname
	
	def generateData(self, obj) :
		data = obj.properties["text"].value.text
		values = data.split("\n")
		tablename = obj.properties["stereotype"].value
		sql = "\n"
		for val in values :
			sql += "INSERT INTO " + tablename + " VALUES (" + val + ");\n"
		
		return sql
			
	
	def printSQL(self) :
		print self.SQL

class DiaSchema :
	
	def __init__(self, name) :
		self.name = name
		self.diagram = dia.new(self.name + ".dia")
		self.data = self.diagram.data
		display = self.diagram.display()
		self.layer = self.data.active_layer

	def addEdmxContainer(self, container) :
		for es in container.EntitySet:
			self.addEntity(es)
		
		for assoc in container.AssociationSet :
			self.addAssociation(assoc)
	
	def addAssociation(self, assoc) :
		oType = dia.get_object_type ("UML - Association")
		#print dir(assoc.association)

		for a in assoc.association.AssociationEnd :
			print edm.EncodeMultiplicity(a.multiplicity)
			#print dir(a)
			"""
			for obj in self.layer.objects :
				if str(obj.type) == "UML - Class" :
					if obj.properties.get("name").value == a :
						o, h1, h2 = oType.create(0,0)
						o.properties["constraint"] = k["constraint_name"]
						idx = 8
						for prop in obj.properties.get("attributes").value :
							if prop[0] == k["column_name"] :
								o.handles[0].connect(obj.connections[idx])
								self.diagram.update_connections(o)
								break
							idx += 2
						for obj2 in self.layer.objects :
							if str(obj2.type) == "UML - Class" :
								if obj2.properties.get("name").value == k["references_table"] :
									idx2 = 9
									for prop2 in obj2.properties.get("attributes").value :
										if prop2[0] == k["references_field"] :
											o.handles[1].connect(obj2.connections[idx2])
											self.diagram.update_connections(o)
											break
										idx2 += 2
									break

						self.layer.add_object (o)
		"""
		
	def addEntity(self, entity) :
		oType = dia.get_object_type ("UML - Class")
		o, h1, h2 = oType.create (0,0) # p.x, p.y
		o.properties["name"] = entity.entityType.name
		o.properties["stereotype"] = entity.name

		attributes = []
		methods = []
		
		for p in entity.entityType.Property :
			name = p.name
			default = ""
			value = ""
			null = "NULL"
			visibility = 0
			atype = p.type
			if p.nullable == False:
				null = "NOT NULL"
							
			if p.name == entity.entityType.Key.PropertyRef[0].name :
				visibility = 2
			
			value += null
			attributes.append((name, atype, value,"",visibility,0,0))

		for n in entity.entityType.NavigationProperty :
			#attributes.append((n.name, "Navigation", "","",0,0,0))
			# (name, type, value, comment, kind)
			params = []
			params.append(("from","",n.fromRole,"",0))
			params.append(("to","",n.toRole,"",0))
			# (name, type, comment, stereotype, visibility, inheritance_type, query,class_scope, params)
			methods.append((n.name, "","","",0,0,0,0,params))


		o.properties["attributes"] = attributes
		o.properties["operations"] = methods
		self.layer.add_object (o)
		

	def addTable(self, table, columns, indices) :
		oType = dia.get_object_type ("UML - Class")
		o, h1, h2 = oType.create (0,0) # p.x, p.y
		o.properties["name"] = table["table_name"]
		attributes = []
		methods = []
				
		for k in columns :
			name = k["column_name"]
			default = ""
			value = ""
			null = "NOT NULL"
			visibility = 0

			atype = k["data_type"]
			if k["character_maximum_length"] != None:
				atype += "(" + str(k["character_maximum_length"]) + ")"
				default = "'"
			
			if k["column_default"] != None :
				value = "DEFAULT " + default + k["column_default"] + default + " "

			if k["is_nullable"] == "YES":
				null = "NULL"
							
			if k["column_name"] == table["column_name"]:
				visibility = 2
			
			value += null
			# (name,type,value,comment,visibility,abstract,class_scope)				
			attributes.append((name, atype, value,"",visibility,0,0))
			
		for ind in indices :
			# index_name attname attnum indisunique indisprimary
			if ind["indisprimary"] != False :
				params = []
				params.append((ind["attname"],"","","",0))
				# (name, type, comment, stereotype, visibility, inheritance_type, query,class_scope, params)
				methods.append((ind["index_name"],"primary key","","",0,0,0,0,params))
			else:			
				if ind["indisunique"] == True :
					itype = "unique index"
				else :
					itype = "index"
					
				# (name, type, value, comment, kind)
				params = []
				params.append((ind["attname"],"","","",0))
				# (name, type, comment, stereotype, visibility, inheritance_type, query,class_scope, params)
				methods.append((ind["index_name"],itype,"","",0,0,0,0,params))
		
		o.properties["attributes"] = attributes
		o.properties["operations"] = methods
		self.layer.add_object (o)
		
	def addViews(self, views) :
		pass
		
	def addSequence(self, seq) :
		# start_value,	increment_by, max_value, min_value
		oType = dia.get_object_type ("UML - SmallPackage")
		o, h1, h2 = oType.create (0,0) # p.x, p.y
		o.properties["stereotype"] = "sequence"
		seqText = "CREATE SEQUENCE " + seq["sequence_name"] + "\n"
		seqText += "START WITH " + str(seq["start_value"]) + "\n"
		seqText += "INCREMENT BY " + str(seq["increment_by"]) + "\n"
		seqText += "NO MINVALUE\n"
		seqText += "NO MAXVALUE\n"
		seqText += "CACHE 1;"
		o.properties["text"] = seqText
		self.layer.add_object (o)
		
		
	def addConstraints(self, keys) :
		oType = dia.get_object_type ("UML - Constraint")
		for k in keys :
			for obj in self.layer.objects :
				if str(obj.type) == "UML - Class" :
					if obj.properties.get("name").value == k["table_name"] :
						o, h1, h2 = oType.create(0,0)
						o.properties["constraint"] = k["constraint_name"]
						idx = 8
						for prop in obj.properties.get("attributes").value :
							if prop[0] == k["column_name"] :
								o.handles[0].connect(obj.connections[idx])
								self.diagram.update_connections(o)
								break
							idx += 2
						for obj2 in self.layer.objects :
							if str(obj2.type) == "UML - Class" :
								if obj2.properties.get("name").value == k["references_table"] :
									idx2 = 9
									for prop2 in obj2.properties.get("attributes").value :
										if prop2[0] == k["references_field"] :
											o.handles[1].connect(obj2.connections[idx2])
											self.diagram.update_connections(o)
											break
										idx2 += 2
									break

						self.layer.add_object (o)




