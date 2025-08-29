from torchgen.api.types import typeAndSizeT
import numpy as np
import scan_docs as sd
import cv2
import sqlite3
from work_w_db import *
import sqlite3
import os


def valid_data(data):
    pass


def main():
    all_pages = [] # вся информация (по листам проверки)
    all_works = dict()
    sql_db_path = r'db_dir/ege_works.db'
    excel_db_path = r'user_table/test.xlsx'
    E_tab = ExcelTable(excel_db_path)
    S_tab = SQLTable(sql_db_path)

    if not os.path.exists(excel_db_path):
        E_tab.create_exell_tab(excel_db_path) # user table

    if not os.path.exists(sql_db_path):
        S_tab.create_sql_table(sql_db_path) # database

    #чтение файлов и парсинг
    for page_num in range(1,3):
        img_obj = sd.ImgScaner(f'scans/{page_num}.jpg')
        page_info = img_obj.get_structure_data()
        all_pages.append(page_info)


    for page in all_pages:
        exp_id, works = page
        for work_id, rate in works.items():
            if work_id in all_works.keys():
                all_works[work_id]['exp2'] = [r for r in rate.values()]
                all_works[work_id]['id_exp2'] = exp_id
            else:
                all_works[work_id] = {'exp1': [r for r in rate.values()],'id_exp1': exp_id}

    print(all_works)
    for work_id, rate in all_works.items():
        S_tab.ins_into_sql(work_id,rate)


    for line_id in range(1, 6):
        E_tab.ins_into_exell(S_tab.get_line(line_id))

if __name__ == "__main__":
    main()