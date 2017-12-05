# -*- encoding:utf-8 -*-
import sqlite3


class Objects:
    """
    Класс для конструирования строки запроса к таблице в базе данных
    поле словарь request_obj описывает структуру запроса
    """
    def __init__(self, db, table, request_obj=None):
        """
        Инициализирует базу данных и таблицу к которой будет выполнен запрос
        параметр db строка содержащая путь и название базы данных sqlite3
            пример: "tables.db"
        параметр table строка название таблицы в базе
            пример: "speciality"
        параметр request_obj словарь описывающий структуру запроса,
        содержит по умолчанию структуру запроса "SELECT * FROM table;"
        """
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
        """
        Из словаря request_obj, описывающего структуру запроса, собирает строку запроса
        """
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
        """
          метод который указывается для запроса, позволяет изменить структуру данных возвращаемых запросом
          как список записей, где каждая запись это словарь, стандартный метод sqlite3.Row не позволяет
          изменять структуру словаря
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def run(self):
        """
            Структура запроса, описанная в словаре request_obj конвертируется в строку и запрос выполняется
            к таблице в базе данных, возвращает результат запроса - список записей
        """
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
        """
        Объединяет 2 значения в одну строку с учетом типов данных
            пример: "name" и "Вася" в строку 'name="Вася"'
                    "age" и  25     в строку "age=25"
        Нужна для формирования параметров sql запроса
        """
        return '%s="%s"' % (key, val) if type(val) and type("str") else '%s=%s' % (key, val)

    def get(self, **kwargs):
        """
        Формирует sql-запрос на получение одной записи из бд по указанным параметрам словаря kwargs
        """
        if len(kwargs):
            where_params = [self.unite(key, val) for key, val in kwargs.items()]
            self.request_obj["WHERE"] = where_params
        self.request_obj["LIMIT"] = 1
        return Objects(self.db, self.table, self.request_obj)

    def filter(self, **kwargs):
        """
        Формирует sql-запрос на получение нескольких записей из бд по указанным параметрам словаря kwargs
        """
        if len(kwargs):
            where_params = [self.unite(key, val) for key, val in kwargs.items()]
            self.request_obj["WHERE"] = where_params
        return Objects(self.db, self.table, self.request_obj)

    def all(self):
        """
        Формирует sql-запрос на получение всех записей таблицы
        """
        self.request_obj["WHERE"] = []
        self.request_obj["LIMIT"] = False
        return Objects(self.db, self.table, self.request_obj)

    def order_by(self, *args):
        """
        Дополняет sql-запрос параметрами сортировки указанными в списке args
        если у параметра в начале указан знак "-" то значит сортировка в порядке убывания DESC
        """
        order_params = [(param[1:] + " DESC") if param[0] == "-" else param for param in args]
        if self.request_obj["LIMIT"] == 1:
            self.request_obj["LIMIT"] = False
        self.request_obj["ORDER BY"] = order_params
        return Objects(self.db, self.table, self.request_obj)

    def values(self, *args):
        """
        Дополняет sql-запрос полями указанными в args, которые будут в записях
        """
        self.request_obj["SELECT"] = [param for param in args]
        return Objects(self.db, self.table, self.request_obj)


class BaseORM:
    """
    Класс для загрузки массива данных в sqlite3.db и работы с этими данными через ORM методы класса
    """

    def __init__(self, db, table):
        """
        Конструктор класса должен получить информацию о sql-таблице, с которой будет производиться работа
        параметр db строка содержащая путь и название базы данных sqlite3
            пример: "tables.db"
        параметр table словарь, с обязательными полями NAME и СOLUMNS, описывающий структуру таблицы
            пример:
               table = {
              "NAME": "table_name",
              "COLUMNS": [
                  "table_column_1 VARCHAR(255)",
                  "table_column_2 INTEGER",
              "FOREIGN_KEYS": [
                  ("table_column_1", "related_table", "related_column"),
                ],
              }
        """
        self.db = db
        self.table = table
        self.objects = Objects(db, table["NAME"])
        self.table_create()

    def execute(self, request):
        """
        Выполняет sql запрос к таблице
        параметр request строка содержащая тело запроса
            пример: "SELECT * FROM table;"
        """
        connection = sqlite3.connect(self.db)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(request)
        connection.commit()
        result = cursor.fetchall()
        connection.close()
        return result

    def table_create(self):
        """
        Создает таблицу в базе, если она еще не существет, со структурой переднной в параметре table
        """
        columns = ', '.join([column for column in self.table["COLUMNS"]])
        sql_create_table = "CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, %s" % (self.table["NAME"], columns)
        if self.table.get("FOREIGN_KEYS") and len(self.table["FOREIGN_KEYS"]):
            for fk in self.table["FOREIGN_KEYS"]:
                sql_create_table += ", FOREIGN KEY (%s) REFERENCES %s (%s)" % (fk[0], fk[1], fk[2])
        sql_create_table += ")"
        self.execute(sql_create_table)
        print(sql_create_table)

    def insert_records(self, records_list):
        """
        Записывает данные, указанные в параметре двумерном массиве records_list, в таблицу в базе данных
        При этом каждая строка массива это запись
        """
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
