import os.path

from openpyxl import *


class ExcelTable():
    def __init__(self, excel_path):
        self.path = excel_path
        self.wb = Workbook()
        self.ws = self.wb.active
        pass

    def create_exell_tab(self):

        if os.path.exists("user_table/test.xlsx"):
            os.remove("user_table/test.xlsx")
        res_table_headers = ["WORK_ID",
                             "E1 N1", "E1 N2", "E1 N3", "E1 N4", "E1 N5", "E1 N6",
                             "E2 N1", "E2 N2", "E2 N3", "E2 N4", "E2 N5", "E2 N6",
                             'id_exp1', 'id_exp2', "mistake", "n_w_mistake"]
        for name, col in enumerate("ABCDEFGHIJKLMNOPQ", start=0):
            self.ws[f'{col}1'] = res_table_headers[name]
        self.wb.save(self.path)
        pass


    def excel_safe_value(self, value):
        """Преобразует значение для безопасной записи в Excel"""
        if value is None:
            return ""

        if isinstance(value, (str, bool)):
            return value

        if isinstance(value, (int, float)):
            if abs(value) > 1e15:
                return f"'{value}"
            return value

        if isinstance(value, (dict, list)):
            return str(value)

        return str(value)

    def fill_all(self,work_info:list[list]):
        for line in work_info:
            self.ws.append(line)
        self.wb.save(self.path)
        pass


