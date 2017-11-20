# -*- encoding:utf-8 -*-
from libs import TableConstructor
from libs.TableLoader import BaseTL
from libs.Sqlite3_ORM import BaseORM


class TL(BaseTL, BaseORM):

    def __init__(self, table, db="tables.db"):
        BaseORM.__init__(self, db, table)
        BaseTL.__init__(self)

    def insert_records(self, url, selector, excluded_columns_indexes=None):
        rows_list = self.load_table_rows(url, selector, excluded_columns_indexes)
        BaseORM.insert_records(self, rows_list)

# ------
url_applicant = 'http://abit.susu.ru/rating/spis_27072015.php'
selector_applicant = {'class': 'tbbig'}  # css selector
table_applicant = {
          "NAME": "applicant",
          "COLUMNS": [
              "speciality VARCHAR(255)",
              "reg_number INTEGER",
              "name VARCHAR(255)",
              "doc_category VARCHAR(255)",
              "app_category VARCHAR(255)",
              "priority INTEGER",
              "total_score INTEGER",
              "subjects VARCHAR(255)",
              "achiev_type VARCHAR(255)",
              "achiev_score INTEGER"
          ],
          "FOREIGN_KEYS": [
              ("speciality", "speciality", "code"),
            ],
          }
# ------------
url_subject = 'http://abit.susu.ru/exam/minball_c.php'
selector_subject = {'class': 'tbsmall'}
table_subject = {
          "NAME": "subject",
          "COLUMNS": [
              "name VARCHAR(255)",
              "value INTEGER",
          ]
        }
# -------------
url_speciality = 'http://abit.susu.ru/stat/ball_konk/ball_2017.php'
selector_speciality = {'class': 'tb'}
table_speciality = {
          "NAME": "speciality",
          "COLUMNS": [
               "code VARCHAR(10)",
               "name VARCHAR(255)",
               "budget_places INTEGER",
               "all_priority FLOAT",
               "one_priority FLOAT",
               "cut_score INTEGER"
          ]
        }
# ---------------
applicant = TL(table_applicant)
# applicant.insert_records(url_applicant, selector_applicant, [0, 2])

subject = TL(table_subject)
# subject.insert_records(url_subject, selector_subject)

speciality = TL(table_speciality)
# speciality.insert_records(url_speciality, selector_speciality, [0, ])

result_tables = list()
applicant_name = "Колянов Илья Игоревич"
applicant_entries = applicant.objects.filter(name=applicant_name).run()
applicant_entries_tbody = list()
speciality_tables = []

for entry in applicant_entries:
    entry_speciality = speciality.objects.get(code=entry["speciality"]).values("name", "budget_places", "code", "cut_score").run()
    entry_speciality_applicants = applicant.objects.filter(speciality=entry_speciality["code"]).order_by("-total_score").values("name", "total_score").run()
    entry_speciality_rank = False
    entry_style = dict()
    for i in range(len(entry_speciality_applicants)):
        if applicant_name in entry_speciality_applicants[i]["name"]:
            entry_speciality_rank = i
            if entry_speciality_rank > entry_speciality["budget_places"]:
                entry_style["background-color"] = "#ff9773"
            else:
                entry_style["background-color"] = "greenyellow"
            entry_speciality_applicants[i]["style"] = entry_style

    entry_row = {
        "priority": entry["priority"],
        "name": entry_speciality["name"],
        "cut_score": "%s (есть %s)" % (entry_speciality["cut_score"], entry["total_score"]),
        "budget_places": entry_speciality["budget_places"],
        "rank": "%s (из %s)" % (entry_speciality_rank, len(entry_speciality_applicants)),
        "style": entry_style,
    }
    applicant_entries_tbody.append(entry_row)

    speciality_tbody = list()
    range_start = entry_speciality_rank - 5 if (entry_speciality_rank - 5) >= 0 else 0
    range_end = entry_speciality_rank + 5 if (entry_speciality_rank + 5) < len(entry_speciality_applicants) else len(entry_speciality_applicants)
    for i in range(range_start, range_end):
        entry_speciality_applicants[i]["rank"] = i + 1
        speciality_tbody.append(entry_speciality_applicants[i])
    speciality_thead = [
        ("rank", "Место<br>в рейтинге"),
        ("name", "ФИО абитурьента"),
        ("total_score", "баллы"),
    ]
    speciality_table = {
        "title": 'Рейтинг по специальности "%s"' % entry_speciality["name"],
        "thead": speciality_thead,
        "tbody": speciality_tbody,
    }
    speciality_tables.append(speciality_table)

# ------ table 1
applicant_entries_thead = [
    ("priority", "Приоритет"),
    ("name", "Имя"),
    ("cut_score", "Проходной балл"),
    ("budget_places", "Бюджетных<br>мест"),
    ("rank", "Место<br>в рейтинге"),
    ]

applicant_entries_table = {
    "title": "Рейтинг абитурьента %s" % applicant_name,
    "thead": applicant_entries_thead,
    "tbody": applicant_entries_tbody,
}
result_tables.append(applicant_entries_table)
for table in speciality_tables:
    result_tables.append(table)
# ------ таблицы специальностей
TableConstructor.create(result_tables, "templates/entries.html")

# ------ server start
from http.server import HTTPServer, CGIHTTPRequestHandler
server_address = ("localhost", 8000)
httpd = HTTPServer(server_address, CGIHTTPRequestHandler)
httpd.server_activate()
httpd.server_close()

try:
    httpd.serve_forever()
except:
    pass