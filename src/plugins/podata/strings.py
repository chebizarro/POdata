class podata_sql :
	tables = """SELECT tc.constraint_name,
						  tc.table_name,
						  kcu.column_name
					 FROM information_schema.table_constraints tc
				LEFT JOIN information_schema.key_column_usage kcu
					   ON tc.constraint_catalog = kcu.constraint_catalog
					  AND tc.constraint_name = kcu.constraint_name
					  WHERE tc.constraint_type = 'PRIMARY KEY';""",
	
	orderby = "' ORDER BY ordinal_position;",
	
	indices = """SELECT a.index_name, 
						b.attname,
						 b.attnum,
						 a.indisunique,
						 a.indisprimary
				FROM ( SELECT a.indrelid,
							a.indisunique,
							a.indisprimary, 
							c.relname index_name, 
						unnest(a.indkey) index_num 
						FROM pg_index a, 
								  pg_class b, 
								  pg_class c 
							WHERE b.relname=%s 
							  AND b.oid=a.indrelid 
							  AND a.indexrelid=c.oid 
						 ) a, 
						 pg_attribute b 
					WHERE a.indrelid = b.attrelid 
					AND a.index_num = b.attnum 
					ORDER BY a.index_name, 
						 a.index_num""",

	columns = """SELECT ordinal_position,
					column_name,
					data_type,
					column_default,
					is_nullable,
					character_maximum_length,
					numeric_precision
				FROM information_schema.columns
				WHERE table_name = '""",
				
	fkeys = """	SELECT tc.constraint_name,
							  tc.constraint_type,
							  tc.table_name,
							  kcu.column_name,
							  ccu.table_name AS references_table,
							  ccu.column_name AS references_field
						 FROM information_schema.table_constraints tc
					LEFT JOIN information_schema.key_column_usage kcu
						   ON tc.constraint_catalog = kcu.constraint_catalog
						  AND tc.constraint_schema = kcu.constraint_schema
						  AND tc.constraint_name = kcu.constraint_name
					LEFT JOIN information_schema.referential_constraints rc
						   ON tc.constraint_catalog = rc.constraint_catalog
						  AND tc.constraint_schema = rc.constraint_schema
						  AND tc.constraint_name = rc.constraint_name
					LEFT JOIN information_schema.constraint_column_usage ccu
						   ON rc.unique_constraint_catalog = ccu.constraint_catalog
						  AND rc.unique_constraint_schema = ccu.constraint_schema
						  AND rc.unique_constraint_name = ccu.constraint_name
					WHERE tc.constraint_type = 'FOREIGN KEY'""",
					
	sequences = "SELECT c.relname FROM pg_class c WHERE c.relkind = 'S'",
	
	sequence_inf = "SELECT sequence_name, start_value, increment_by, max_value, min_value FROM "
