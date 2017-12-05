# -*- encoding:utf-8 -*-


def create(tables_data, file_name="templates/result.html"):
    """
    Формирует html файл содержащий таблицы, данные которых переданны в списке таблиц tables_data
    пример: tables_data
        [
            {   # 1 таблица
                "title": "Рейтинг абитурьента Вася",
                "thead": [   # Заголовок таблицы
                            ("priority", "Приоритет"),
                            ("name", "Имя"),
                ],
                "tbody": [
                            {   # 1 строка таблицы
                                "priority": "содержимое колонки priority",
                                "name": "содержимое колонки name",
                                "style":
                                        {"background-color": "greenyellow",
                                },
                            },
                            {   # 2 строка таблицы
                                "priority": "содержимое колонки priority",
                                "name": "содержимое колонки name",
                                "style":
                                        {"background-color": "orange",
                                },
                            },

                ],
            },
            {
               ... # вторая таблица
            },
        ]
    """
    tables = list()
    for table_data in tables_data:
        thead_cols = "".join(["<th>%s</th>" % col[1] for col in table_data["thead"]])
        thead = "<tr>%s</tr>" % thead_cols
        tbody = ""
        for row in table_data["tbody"]:
            if not row.get("style"):
                row["style"] = dict()
            tbody_cols = list()
            for column in table_data["thead"]:
                column_name = column[0]
                tbody_cols.append("<td>%s</td>" % row[column_name])
            row_style = ['%s:%s' % (key, val) for key, val in row["style"].items()]
            row_style = ";".join(row_style)
            tbody_row = '<tr style="%s">%s</tr>' % (row_style, "".join(tbody_cols))
            tbody += tbody_row
        table = "<h2>%s</h2><table>%s%s</table>" % (table_data["title"], thead, tbody)
        tables.append(table)

    html_content = '''
    <!DOCTYPE html>
    <html lang="ru-RU">
        <head>
            <meta charset="UTF-8">
            <title>Easy html</title>
            <link rel="stylesheet" href="../static/style.css">
        </head>
        <body>
            <div class='container'>
                %s
            </div>
        </body>
    </html>
    ''' % "".join(tables)
    file = open(file_name, 'w', encoding="utf-8")
    file.write(html_content)
    file.close()
    return True


"""
Чтобы поднять сервер, в python консоли выпоните команды:

from http.server import HTTPServer, CGIHTTPRequestHandler
server_address = ("localhost", 8000)
httpd = HTTPServer(server_address, CGIHTTPRequestHandler)
httpd.server_activate()
httpd.serve_forever()

Запустится http - сервер
В браузере откройте страницу localhost:8000 и откройте нужную страницу
"""