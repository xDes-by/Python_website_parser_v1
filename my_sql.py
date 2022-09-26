import sqlite3

my_SQL_name_file = 'parse_base.db'


class MySQL:
    def __init__(self):
        self.connect = sqlite3.connect(my_SQL_name_file, check_same_thread=False)

    def create_table(self, name, param):
        if not name or not param: return
        try:
            self.connect.execute(f"CREATE TABLE {name} ({param})")
            print(f"База данных {name} создана")
        except:
            pass

    def table_get(self, name, param, data):
        if not name: return None
        if not param or not data:
            return self.connect.execute(f"SELECT * FROM {name}").fetchall()
        else:
            return self.connect.execute(f"SELECT * FROM {name} WHERE {param} = ?", (data,)).fetchall()

    def table_get_all(self):
        return self.connect.execute(f"SELECT * FROM my_sql_banana").fetchall()

    def table_insert(self, name, param):
        # print(name)
        # print(param)
        if not name or not param: return
        # print(int(len(param) - 1))
        len_param = '?, ' * int(len(param) - 1) + "?"
        self.connect.execute(f"INSERT INTO {name} VALUES (NULL, {len_param})", param)
        self.connect.commit()

    def table_update(self, name, find_data, new_data):
        if not name: return None
        if not find_data or not new_data: return
        data = []
        new_data_str = ""
        for i in new_data:
            new_data_str += f'{i} = ?, '
            data.append(new_data[i])
        new_data_str += 'end'
        new_data_str = new_data_str.replace(f'?, end', '?')
        find_data_str = ""
        for i in find_data:
            find_data_str += f'{i} = ?, '
            data.append(find_data[i])
        find_data_str += 'end'
        find_data_str = find_data_str.replace(f'?, end', '?')
        self.connect.execute(f"UPDATE {name} SET {new_data_str} WHERE {find_data_str}", tuple(data))
        self.connect.commit()

    def table_delete(self, name, param):
        print(name)
        print(param)
        if not name or not param: return
        self.connect.execute(f"DELETE FROM {name} WHERE article_number = {param}")
        self.connect.commit()


my_sql = MySQL()
