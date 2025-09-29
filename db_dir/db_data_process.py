class DataProcess:
    def __init__(self, db_path):
        self.db_path = db_path
        pass

    def list_for_ResTable(self, user_info: list) -> list:
        res_list = [user_info[0]]
        rates = user_info[1]['exp1'] + user_info[1]['exp2']
        res_list.extend(rates)
        res_list.extend([user_info[1]['id_exp1'], user_info[1]['id_exp2']])
        return res_list

    def check_rates(self, studen_info:list) -> list:
        studen_info = list(studen_info)
        mistakes = 0
        nums_w_mistake = ''
        rates = studen_info[1:-2]
        for i in range(len(rates) // 2):
            rate_exp1, rate_exp2 = rates[i], rates[i + 6]
            if 'X' in [rate_exp1, rate_exp2]:
                if rate_exp1 != rate_exp2:
                    mistakes += 1
                    nums_w_mistake += str(i+1) + ' '
            else:
                if abs(int(rate_exp1) - int(rate_exp2)) >= 2:
                    mistakes += 1
                    nums_w_mistake += str(i + 1) + ' '
        processed = studen_info + [mistakes, nums_w_mistake]
        return processed