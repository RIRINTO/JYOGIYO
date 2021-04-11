import cx_Oracle
import mybatis_mapper2sql
import configparser

class DaoBuy:
    def __init__(self, config_path='config.ini', xml_path='dao/buy.xml'):
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml=xml_path)[0]
        
    def selectAll(self, buy_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        rs = self.cs.execute(sql,(buy_seq,))
        list = []
        for record in rs:
            list.append({'buy_seq':record[0],'menu_seq':record[1],'buy_cnt':record[2], 'in_date':record[7],
                         'in_user_id':record[8],'up_date':record[9], 'up_user_id':record[10]})
        return list

    def select(self, buy_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "select")
        rs = self.cs.execute(sql,(buy_seq,))
        list = []
        for record in rs:
            list.append({'buy_seq':record[0],'menu_seq':record[1],'buy_cnt':record[2], 'in_date':record[7],
                         'in_user_id':record[8],'up_date':record[9], 'up_user_id':record[10]})
        return list

    def insert(self, buy_seq, menu_seq, buy_cnt, in_date, in_user_id, up_date, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "insert")
        self.cs.execute(sql, (menu_seq, buy_cnt, in_user_id, up_user_id))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def update(self, buy_seq, menu_seq, buy_cnt, in_date, in_user_id, up_date, up_user_id):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "update")  
        self.cs.execute(sql, (menu_seq, buy_cnt, up_user_id, buy_seq))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt

    def delete(self, buy_seq):
        sql = mybatis_mapper2sql.get_child_statement(self.mapper, "delete") 
        self.cs.execute(sql, (buy_seq,))
        self.conn.commit()
        cnt = self.cs.rowcount
        return cnt    
        
if __name__ == "__main__":
    dao = DaoBuy(config_path='../config.ini', xml_path='buy.xml')
#     list = dao.insert("1", "1", "1", " ", "1", " ", "1")
#     list = dao.update("21", "1", "3434", " ", "1", " ", "1")
#     list = dao.delete("21")
#     print(list)