# -*- encoding:utf-8 -*-
from urllib import request
from bs4 import BeautifulSoup
from re import sub


class BaseTL:

    def __init__(self):
        self.bad_chars = "^\s+|\n|\r|\s+$"

    def clear(self, text):
        return sub(self.bad_chars, '', text) if text else None

    def load_table_rows(self, url, selector=None, excluded_columns_indexes=None):
        file = request.urlopen(url)
        soup = BeautifulSoup(file, 'lxml')
        table = soup.find('table', selector) if selector else soup.find('table')
        rows = table.find_all('tr')
        rows_list = list()
        for row in rows[1:]:
            columns = row.find_all('td')
            if excluded_columns_indexes:
                # Удалим столбцы, которые не должны попасть в бд
                offset = 0
                for i in excluded_columns_indexes:
                    del columns[i - offset]
                    offset += 1
            rows_list.append([self.clear(column.text) for column in columns])
        return rows_list
