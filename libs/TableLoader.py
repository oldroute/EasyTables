# -*- encoding:utf-8 -*-
from urllib import request
from bs4 import BeautifulSoup
from re import sub


class BaseTL:

    def __init__(self):
        self.bad_chars = "^\s+|\t|\n|\r|\s+$"

    def clear(self, text):
        """
        Удаляет спец. символы и лишние пробелы из строки
        """
        return sub(self.bad_chars, '', text) if text else None

    def load_table_rows(self, url, selector=None, excluded_columns_indexes=None):
        """
        1 Получает html-страницу, по указанной строке url, как текст
            пример url: 'http://abit.susu.ru/stat/ball_konk/ball_2017.php'
        2 В тексте страницы находит первую таблицу
        ( Если указанн словарь css-selector то ищет таблицу с указанным селектором)
            аример selector: {'class': 'tb'}
        3. В найденной таблице все столбцы строк, кроме первой строки, загружает в массив
        Если передан массив excluded_columns_indexes, то в конечном массиве данных не будет колонок
        таблицы с указанными в параметре номерами
            пример excluded_columns_indexes: [0,2]
        """
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
