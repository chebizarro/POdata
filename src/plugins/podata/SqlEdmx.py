import pyslet.odata2.csdl as edm
import pyslet.odata2.metadata as edmx

import psycopg2
import psycopg2.extras

#import the sql strings
from strings import podata_sql as sql

class SqlEdmx :
	
	def __init__(self, config) :
		self.doc = edmx.Document()
		self.parse_db(config)
		return self.doc
	
	def create_dataservice(self) :
		dataService = edmx.Edmx(self.doc)

	def create_schema(self) :
		schema = edm.Schema()
		schema.name = config["dbname"].capitalize()
	
	def create_entity_container(self) :
		ec = edm.EntityContainer(self.doc)
		ec.name = config["dbname"].capitalize() + "Container"
		ec.SetAttribute("IsDefaultEntityContainer", "true")
		
	def create_entity_set(self) :
		pass
		
	def create_association_set(self) :
		pass
		
	def create_function_import(self) :
		pass
		
	def create_end(self) :
		pass
	def create_entity_type(self) :
		pass
		
	def create_property(self) :
		pass

	def create_navigation_property(self) :
		pass
		
	def create_complex_type(self) :
		pass
		
	def create_association(self) :
		pass
	
	def parse_tables(self) :
		self.cursor.execute(sql.tables)
		tables = self.cursor.fetchall()

		for t in tables:
			tableName = t["table_name"]
			tableColumns = sql.columns + tableName + sql.orderby
			self.cursor.execute(tableColumns)
			columns = self.cursor.fetchall()
			
			self.cursor.execute(sql.indices, (tableName,))
			indices = self.cursor.fetchall()
			
			#diagram.addTable(t, columns, indices)

	def parse_keys(self) :
		self.cursor.execute(sql.fkeys)          
		fkeys = self.cursor.fetchall()
		#diagram.addConstraints(fkeys)


	def parse_sequences(self) :
		self.cursor.execute(sql.sequences)          
		seqs = self.cursor.fetchall()
		
		for s in seqs :
			self.cursor.execute(sql.squence_inf)
			seqInf = self.cursor.fetchall()
			#diagram.addSequence(seqInf[0])

	def parse_db(self, config) :
		con = None
		try:
			con = psycopg2.connect("dbname='"+config["dbname"] + "' "
				+ "user='" + config["user"] + "' "
				+ "password='" + config["password"] + "' "
				+ "host='" + config["host"] + "' "
				+ "port='" + config["port"] + "'") 
			
			self.cursor = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)



			
			
			self.cursor.execute(sql.indices, (tableName,))
			indices = self.cursor.fetchall()
 
			
			self.parse_tables()
			self.parse_keys()
			self.parse_sequences()
	
						
		except psycopg2.Error, e:
			dia.message(2, str(e))
			# still need to sort this mess out
			#print str(e)
			#sys.exit(1)
		
		finally:		
			if con:
				con.close()
			self.quit(None, None)
