import sqlite3


class Database:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.scheme_tables = {
            "bar": ("category", "name", "photo_link", "taste", "info", "glass"),
            "info": ("category", "name", "photo_link", "info"),
            "cuisine": ("category", "name", "photo_link", "description", "rus_description", "extra_info", "serving"),
            "shibui": ("category", "name", "photo_link", "description", "rus_description", "extra_info", "serving"),
            "alcohol": ("category", "name", "photo_link", "abv", "taste", "serving", "history"),
        }

    def execute(self, query: str, params: tuple = (), fetchone=False, fetchall=False):
        with self.connection:
            cursor = self.connection.execute(query, params)
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()

    def create_table_bar(self):
        self.execute("""CREATE TABLE bar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    photo_link TEXT,
    taste TEXT,
    info TEXT,
    glass TEXT
);""")

    def create_table_info(self):
        self.execute("""CREATE TABLE info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    photo_link TEXT,
    info TEXT
);""")

    def create_table_cuisine(self):
        self.execute("""CREATE TABLE cuisine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    photo_link TEXT,
    description TEXT,
    rus_description TEXT,
    extra_info TEXT,
    serving TEXT
);""")

    def create_table_shibui(self):
        self.execute("""CREATE TABLE shibui (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    photo_link TEXT,
    description TEXT,
    rus_description TEXT,
    extra_info TEXT,
    serving TEXT
);""")

    def create_table_alcohol(self):
        self.execute("""CREATE TABLE alcohol (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    photo_link TEXT,
    abv TEXT,
    taste TEXT,
    serving TEXT,
    history TEXT
);""")

    def insert_row(self, table: str, row: list):
        row = [x.strip() if isinstance(x, str) else x for x in row]
        placeholders = ', '.join(['?'] * len(row))
        table_names = self.scheme_tables[table]
        query = f"INSERT INTO {table} {table_names} VALUES ({placeholders})"
        self.execute(query, tuple(row))

    def clean_all_values(self):
        for table in self.scheme_tables.keys():
            self.execute(f"DELETE FROM {table}")

    def get_categories(self, table: str):
        query = f"SELECT DISTINCT category FROM {table}"
        result = self.execute(query, fetchall=True)
        return [row["category"] for row in result]

    def get_dishes_by_category(self, table: str, category: str):
        query = f"SELECT name FROM {table} WHERE category = ?"
        result = self.execute(query, params=(category, ), fetchall=True)
        return [row["name"] for row in result]

    def get_dish_detail(self, table: str, dish_name: str):
        query = f"SELECT * FROM {table} WHERE name = ?"
        result = self.execute(query, params=(dish_name, ), fetchone=True)
        return dict(result)

    def get_records_with_photo(self):
        results = []
        for table_name in self.scheme_tables.keys():
            query = f"SELECT id, photo_link FROM {table_name} WHERE photo_link IS NOT NULL AND TRIM(photo_link) != ''"
            records = self.execute(query, fetchall=True)
            for row in records:
                results.append({
                    'table': table_name,
                    'id': row['id'],
                    'photo_link': row['photo_link'],
                })
        return results

    def get_name_by_id(self, table: str, record_id: int):
        query = f"SELECT name FROM {table} WHERE id = ?"
        result = self.execute(query, params=(record_id, ), fetchone=True)
        return result["name"] if result else None
