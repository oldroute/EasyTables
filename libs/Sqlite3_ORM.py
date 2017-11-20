# -*- encoding:utf-8 -*-
import sqlite3


class Objects:

    def __init__(self, db, table, request_obj=None):
        self.db = db
        self.table = table
        if request_obj is None:
            self.request_obj = {
                "SELECT": ["*", ],
                "FROM": table,
                "WHERE": [],
                "ORDER BY": [],
                "LIMIT": False
            }
        else:
            self.request_obj = request_obj

    def construct_request(self):
        request = "SELECT %s " % ", ".join(param for param in self.request_obj["SELECT"])
        request += "FROM %s " % self.request_obj["FROM"]
        if len(self.request_obj["WHERE"]):
            request += "WHERE %s " % " AND ".join(param for param in self.request_obj["WHERE"])
        if self.request_obj["LIMIT"]:
            request += "LIMIT %s " % self.request_obj["LIMIT"]
        if len(self.request_obj["ORDER BY"]):
            request += "ORDER BY %s " % ", ".join(param for param in self.request_obj["ORDER BY"])

        request = request.strip() + ";"
        return request

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def run(self):
        request = self.construct_request()
        print(request)
        connection = sqlite3.connect(self.db)
        connection.row_factory = sqlite3.Row if self.request_obj["SELECT"][0] == "*" else self.dict_factory
        cursor = connection.cursor()
        cursor.execute(request)
        connection.commit()
        if self.request_obj["LIMIT"] == 1:
            result = cursor.fetchone()
        elif self.request_obj["LIMIT"] > 1:
            result = cursor.fetchmany(self.request_obj["LIMIT"])
        else:
            result = cursor.fetchall()
        connection.close()
        return result

    @staticmethod
    def unite(key, val):
        return '%s="%s"' % (key, val) if type(val) and type("str") else '%s=%s' % (key, val)

    def get(self, **kwargs):
        if len(kwargs):
            where_params = [self.unite(key, val) for key, val in kwargs.items()]
            self.request_obj["WHERE"] = where_params
        self.request_obj["LIMIT"] = 1
        return Objects(self.db, self.table, self.request_obj)

    def filter(self, **kwargs):
        if len(kwargs):
            where_params = [self.unite(key, val) for key, val in kwargs.items()]
            self.request_obj["WHERE"] = where_params
        return Objects(self.db, self.table, self.request_obj)

    def all(self):
        self.request_obj["WHERE"] = []
        self.request_obj["LIMIT"] = False
        return Objects(self.db, self.table, self.request_obj)

    def order_by(self, *args):
        order_params = [(param[1:] + " DESC") if param[0] == "-" else param for param in args]
        if self.request_obj["LIMIT"] == 1:
            self.request_obj["LIMIT"] = False
        self.request_obj["ORDER BY"] = order_params
        return Objects(self.db, self.table, self.request_obj)

    def values(self, *args):
        self.request_obj["SELECT"] = [param for param in args]
        return Objects(self.db, self.table, self.request_obj)


class BaseORM:

    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.objects = Objects(db, table["NAME"])
        self.table_create()

    def execute(self, request):
        connection = sqlite3.connect(self.db)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(request)
        connection.commit()
        result = cursor.fetchall()
        connection.close()
        return result

    def table_create(self):
        columns = ', '.join([column for column in self.table["COLUMNS"]])
        sql_create_table = "CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, %s" % (self.table["NAME"], columns)
        if self.table.get("FOREIGN_KEYS") and len(self.table["FOREIGN_KEYS"]):
            for fk in self.table["FOREIGN_KEYS"]:
                sql_create_table += ", FOREIGN KEY (%s) REFERENCES %s (%s)" % (fk[0], fk[1], fk[2])
        sql_create_table += ")"
        self.execute(sql_create_table)
        print(sql_create_table)

    def insert_records(self, records_list):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()

        sql_select_count = "SELECT COUNT(id) FROM %s;" % self.table["NAME"]
        cursor.execute(sql_select_count)
        records_count = cursor.fetchone()[0]
        # Перед загрузкой записей очистим таблицу от пред. значений
        if records_count > 0:
            sql_delete_records = "DELETE FROM %s;" % self.table["NAME"]
            sql_update_sequence = "UPDATE sqlite_sequence SET seq=0  WHERE name='%s';" % self.table["NAME"]
            sql_compress = "VACUUM"
            cursor.execute(sql_delete_records)
            cursor.execute(sql_update_sequence)
            cursor.execute(sql_compress)

        data_placeholder = ','.join('?' * len(self.table["COLUMNS"]))
        columns_names = [column.split(" ")[0] for column in self.table["COLUMNS"]]
        columns_names = ', '.join(columns_names)
        sql_insert = "INSERT INTO %s(%s) VALUES (%s);" % (self.table["NAME"], columns_names, data_placeholder)
        print(sql_insert)

        for record in records_list:
            cursor.execute(sql_insert, record)
        connection.commit()
        connection.close()
