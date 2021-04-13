import cx_Oracle
import mybatis_mapper2sql
import configparser


def buySort(buyList: list):
    if buyList:
        return {'buy_seq': buyList[0],
                'menu_seq': buyList[1],
                'buy_cnt': buyList[2],
                'in_date': buyList[3],
                'in_user_id': buyList[4],
                'up_date': buyList[5],
                'up_user_id': buyList[6]}
    else:
        return None


class DaoBuy:
    def __init__(self, config_path='config.ini', xml_path='dao/buy.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]

    def genBuySeq(self):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "genBuySeq")
        self.cs.execute(sql)
        return self.cs.fetchone()[0]

    def select(self, buy_seq, menu_seq, buy_cnt, in_date, in_user_id, up_date, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        self.cs.execute(sql, (buy_seq, menu_seq, buy_cnt, in_date, in_user_id, up_date, up_user_id))
        return list(map(buySort, self.cs.fetchall()))

    def insert(self, buy_seq, menuList, owner_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        count = 0
        for menu in menuList:
            self.cs.execute(sql, (buy_seq, menu['menu_seq'], menu['count'], owner_seq, owner_seq))
            count += self.cs.rowcount
        self.conn.commit()
        return count
    
    def delete(self, buy_seq, menu_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "delete")
        self.cs.execute(sql, (buy_seq, menu_seq))
        self.conn.commit()
        return self.cs.rowcount


if __name__ == "__main__":
    dao = DaoBuy(config_path='../config.ini', xml_path='buy.xml')
