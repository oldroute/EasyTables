 easyTables: учебный проект для парсинга и обработки html-таблиц
 =================
 Проект содержит следующие библиотеки:
 * libs/TableLoader.py   Содержит класс BaseTL для загрузки html-таблицы в массив данных
 * libs/Sqlite3_ORM.py   Содержит класс BaseORM для загрузки массива данных в sqlite3.db и работы с этими данными через ORM методы класса
 * libs/TableConstructor.py Содержит метод для создания html-таблицы из массива данных 
 
 
 
 Requirements:
 -----------------
 * python3.5
 * urllib3
 * beautifulsoup4
 * lxml
 * psycopg2
