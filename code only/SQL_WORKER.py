import sqlite3
from openpyxl import *
from sympy.core.benchmarks.bench_arit import timeit_Add_xyz


class SQL_db:
    def __init__(self, path):
        self.db_path = path
        self.conn = sqlite3.connect(self.db_path)
        self.curs = self.conn.cursor()
        pass

    def create_students_table(self):
        self.curs.execute("DROP TABLE IF EXISTS students")
        self.curs.execute("""
            CREATE TABLE students(
            N INTEGER PRIMARY KEY AUTOINCREMENT,
            work_id INTEGER UNIQUE,
            E1_N1 integer,
            E1_N2 integer, 
            E1_N3 integer, 
            E1_N4 integer, 
            E1_N5 integer, 
            E1_N6 integer,
            E2_N1 integer,
            E2_N2 integer, 
            E2_N3 integer, 
            E2_N4 integer, 
            E2_N5 integer, 
            E2_N6 integer,   
            id_exp1 integer,
            id_exp2 integer );""")
        self.conn.commit()

    def create_res_table(self):
        self.curs.execute("DROP TABLE IF EXISTS res_table")
        self.curs.execute("""
            CREATE TABLE res_table (
                N INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id INTEGER UNIQUE,
                E1_N1 integer,
                E1_N2 integer, 
                E1_N3 integer, 
                E1_N4 integer, 
                E1_N5 integer, 
                E1_N6 integer,
                E2_N1 integer,
                E2_N2 integer, 
                E2_N3 integer, 
                E2_N4 integer, 
                E2_N5 integer, 
                E2_N6 integer,   
                id_exp1 integer,
                id_exp2 integer, 
                mistake integer, 
                nums_w_mistake string);
                """)
        self.conn.commit()
        pass

    def create_experts_table(self):
        self.curs.execute("""
        CREATE TABLE experts(
            N INTEGER PRIMARY KEY AUTOINCREMENT,
            exp_id INTEGER UNIQUE,
            check_work INTEGER,
            mistakes INTEGER);
        """)
        self.conn.commit()
        pass

    def insert_into_student(self, student_info:list):
        self.curs.execute("""
        INSERT INTO students
        (work_id ,
        E1_N1, E1_N2, E1_N3, E1_N4, E1_N5, E1_N6,
        E2_N1,E2_N2, E2_N3, E2_N4, E2_N5, E2_N6,
        id_exp1, id_exp2 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, student_info)
        self.conn.commit()
        pass

    def insert_into_res(self, res_line:list):
        self.curs.execute("""
                INSERT INTO res_table
                (work_id ,
                E1_N1, E1_N2, E1_N3, E1_N4, E1_N5, E1_N6,
                E2_N1,E2_N2, E2_N3, E2_N4, E2_N5, E2_N6,
                id_exp1, id_exp2, mistake, nums_w_mistake ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?)
                """, res_line)
        self.conn.commit()
        pass

    def get_users_table(self) -> list:
        self.curs.execute(f"SELECT * FROM students")
        res_data = self.curs.fetchall()
        return res_data

    def get_res_table(self) -> list:
        self.curs.execute(f"SELECT * FROM res_table")
        res_data = self.curs.fetchall()
        return res_data


    def close(self):
        self.conn.close()


if __name__ == "__main__":
    import os

    sql_db_path = r'db_dir/ege_works.db'
    excel_db_path = 'user_table/test.xlsx'


    if os.path.exists(sql_db_path): # при запуске этого файла, бд чистится
        os.remove(sql_db_path)
    # user_excel_table = excel_table()
    user_SQL_database = SQL_db(sql_db_path)

    # user table


