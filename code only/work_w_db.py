import os.path
import sqlite3
from openpyxl import *



class SQLTable:
    def __init__(self, db_path):
        self.path = db_path
        self.create_sql_table()

    def create_sql_table(self):
        if os.path.exists(path=self.path):
            os.remove(self.path)
        path = self.path
        db = sqlite3.connect(path)
        curs = db.cursor()
        curs.execute("""
            CREATE TABLE resTable(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_id INTEGER,
            E1Numb1 integer,
            E1Numb2 integer, 
            E1Numb3 integer, 
            E1Numb4 integer, 
            E1Numb5 integer, 
            E1Numb6 integer,
            E2Numb1 integer,
            E2Numb2 integer, 
            E2Numb3 integer, 
            E2Numb4 integer, 
            E2Numb5 integer, 
            E2Numb6 integer,   
            id_exp1 integer,
            id_exp2 integer );""")
        db.commit()
        db.close()
        pass

    def get_line(self, line_numb: int):
        sql_db_path = self.path
        db = sqlite3.connect(sql_db_path)
        curs = db.cursor()

        curs.execute(f"SELECT * FROM resTable WHERE id = ?", (line_numb,))

        raw = curs.fetchone()
        # print(raw)
        return raw

    def ins_into_sql(self, work_id, rates):
        db = sqlite3.connect('db_dir/ege_works.db')
        curs = db.cursor()

        curs.execute(f"""INSERT INTO resTable (work_id, E1Numb1, E1Numb2,E1Numb3,E1Numb4,E1Numb5,E1Numb6,E2Numb1,E2Numb2,
        E2Numb3,E2Numb4,E2Numb5,E2Numb6, id_exp1, id_exp2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """,
                     (work_id,
                      rates['exp1'][0], rates['exp1'][1], rates['exp1'][2], rates['exp1'][3], rates['exp1'][4],
                      rates['exp1'][5],
                      rates['exp2'][0], rates['exp2'][1], rates['exp2'][2], rates['exp2'][3], rates['exp2'][4],
                      rates['exp2'][5],
                      rates['id_exp1'], rates['id_exp2'])
                     )
        db.commit()
        db.close()
        pass





if __name__ == "__main__":
    tab = SQLTable('db_dir/ege_works.db')
    tab.create_sql_table()
