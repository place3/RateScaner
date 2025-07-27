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
    excel_db_path = 'user_table/test.xlsx'

    if not os.path.exists(excel_db_path):
        create_exell_tab(excel_db_path) # user table

    if not os.path.exists(sql_db_path):
        create_sql_table(sql_db_path) # database

    #чтение файлов и парсинг
    for page_num in range(1,3):
        img = sd.get_img(f'scans/{page_num}.jpg')
        page_info = sd.get_structure_data(img, sd.get_ROIs('ROIs.json'), page_num)
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
        ins_into_sql(work_id,rate)


    for line_id in range(1, 6):
        ins_into_exell(get_line(line_id, sql_db_path),  excel_db_path)

if __name__ == "__main__":
    main()