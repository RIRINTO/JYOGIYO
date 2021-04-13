import cx_Oracle
import mybatis_mapper2sql
import configparser


def menuSort(menuList: list):
    if menuList:
        return {"menu_seq": menuList[0],
                "owner_seq": menuList[1],
                "cate_seq": menuList[2],
                "menu_name": menuList[3],
                "menu_price": menuList[4],
                "menu_content": menuList[5],
                "menu_display_yn": menuList[6],
                "attach_path": menuList[7],
                "attach_file": menuList[8],
                "in_date": menuList[9],
                "in_user_id": menuList[10],
                "up_date": menuList[11],
                "up_user_id": menuList[12],
                "cate_name": menuList[13]}
    return None


class DaoMenu:
    def __init__(self, config_path='config.ini', xml_path='dao/menu.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]

    def selectAll(self, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "selectAll")
        self.cs.execute(sql, (owner_seq,))
        return list(map(menuSort, self.cs.fetchall()))

    def selectFromKiosk(self, owner_seq, cate_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "selectFromKiosk")
        self.cs.execute(sql, (owner_seq, cate_seq))
        return list(map(menuSort, self.cs.fetchall()))

    def select(self, menu_seq, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        self.cs.execute(sql, (menu_seq, owner_seq))
        return menuSort(self.cs.fetchone())

    def insert(self, owner_seq, cate_seq, menu_name, menu_price, menu_content, menu_display_yn, attach_path, attach_file):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        self.cs.execute(sql, (owner_seq, cate_seq, menu_name, menu_price, menu_content, menu_display_yn, attach_path, attach_file, owner_seq, owner_seq))
        self.conn.commit()
        return self.cs.rowcount

    def update(self, cate_seq, menu_name, menu_price, menu_content, menu_display_yn, attach_path, attach_file, up_user_id, menu_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "update")
        self.cs.execute(sql, (cate_seq, menu_name, menu_price, menu_content, menu_display_yn, attach_path, attach_file, up_user_id, menu_seq))
        self.conn.commit()
        return self.cs.rowcount


if __name__ == '__main__':
    daoMenu = DaoMenu(config_path='../config.ini', xml_path='menu.xml')
