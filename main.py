from torchgen.api.types import typeAndSizeT
import numpy as np
import scan_docs as sd
import cv2
import sqlite3
from work_w_db import *
import sqlite3
import os
from db_dir.SQL_WORKER import SQL_db
from db_dir.db_data_process import *
from db_dir.EXCEL_WORKER import ExcelTable
import matplotlib.pyplot as plt


def valid_data(data):
    pass


def main():
    all_pages = []  # вся информация (по листам проверки)
    all_works = dict()
    sql_db_path = r'db_dir/ege_works.db'
    excel_db_path = r'user_table/test.xlsx'
    E_tab = ExcelTable(excel_db_path)
    db = SQL_db(sql_db_path)



    # чтение файлов и парсинг
    for page_num in range(1, 3):
        img_obj = sd.ImgScaner(f'scans/{page_num}.jpg')
        page_info = img_obj.get_structure_data()
        plt.imshow(img_obj.img, cmap="gray")
        # plt.show()
        # plt.close()
        all_pages.append(page_info)

    print('работы прочтаны')

    #Реструктурирование прочитанной информации
    for page in all_pages:
        exp_id, works = page
        for work_id, rate in works.items():
            if work_id in all_works.keys():
                all_works[work_id]['exp2'] =  [r for r in rate.values()]
                all_works[work_id]['id_exp2'] =  exp_id
            else:
                all_works[work_id] = {'exp1': [r for r in rate.values()], 'id_exp1': exp_id}


    #Занесение информации об учениках в БД
    db.create_students_table()
    db.create_res_table()
    data_proc = DataProcess(sql_db_path)
    for work_id, rate in all_works.items():
        res_line = data_proc.list_for_ResTable([work_id,rate])
        db.insert_into_student(res_line)

    #Обработка информации и занесение в БД
    all_processed_lines = []
    for line in db.get_users_table():
        process_line = data_proc.check_rates(line[1:])
        db.insert_into_res(process_line)
        all_processed_lines.append(process_line)

    #Создание пользовательской таблицы
    E_tab.create_exell_tab()
    E_tab.fill_all(all_processed_lines)


    # for line_id in range(1, 6):
    #     E_tab.ins_into_exell(S_tab.get_line(line_id))

    db.close()

if __name__ == "__main__":
    main()
