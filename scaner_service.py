import sys

from CORE import scan_docs as sd
from work_w_db import *
import os
from CORE.scan_docs import CNNOCR
from db_dir.SQL_WORKER import SQL_db
from db_dir.db_data_process import *
from db_dir.EXCEL_WORKER import ExcelTable
import matplotlib.pyplot as plt





















def run_scan(n_pages: int = 2,
             scans_root: str = "",
             res_path: str = "") -> str:
    all_pages = []  # вся информация (по листам проверки)
    all_works = dict()
    sql_db_path = r'C:\Users\us3r02\PycharmProjects\ege_doc_scan\db_dir\ege_works.db'
    excel_db_path = os.path.join(res_path, 'res_table.xlsx')
    E_tab = ExcelTable(excel_db_path)
    db = SQL_db(sql_db_path)

    # чтение файлов и парсинг
    for page in os.listdir(scans_root):
        if page.endswith('txt'):
            continue
        img_obj = sd.ImgScanner(os.path.join(scans_root, page), ocr_mode=CNNOCR())
        page_info = img_obj.get_structure_data()
        plt.imshow(img_obj.img, cmap="gray")
        plt.show()
        plt.close()
        all_pages.append(page_info)

    print('работы прочтаны')

    # Реструктурирование прочитанной информации
    for page in all_pages:
        exp_id, works = page
        for work_id, rate in works.items():
            if work_id in all_works.keys():
                all_works[work_id]['exp2'] = [r for r in rate.values()]
                all_works[work_id]['id_exp2'] = exp_id
            else:
                all_works[work_id] = {'exp1': [r for r in rate.values()], 'id_exp1': exp_id}

    # Занесение информации об учениках в БД
    db.create_students_table()
    db.create_res_table()
    data_proc = DataProcess(sql_db_path)
    for work_id, rate in all_works.items():
        res_line = data_proc.list_for_ResTable([work_id, rate])
        db.insert_into_student(res_line)

    # Обработка информации и занесение в БД
    all_processed_lines = []
    for line in db.get_users_table():
        process_line = data_proc.check_rates(line[1:])
        db.insert_into_res(process_line)
        all_processed_lines.append(process_line)

    # Создание пользовательской таблицы
    E_tab.create_exell_tab()
    E_tab.fill_all(all_processed_lines)

    # for line_id in range(1, 6):
    #     E_tab.ins_into_exell(S_tab.get_line(line_id))

    db.close()
    if not os.path.exists(res_path):
        return ""
    return res_path


if __name__ == "__main__":
    SCANS_PATH = sys.argv[1]
    RES_OUTPUT = sys.argv[2]
    print(run_scan(scans_root=SCANS_PATH, res_path=RES_OUTPUT))
