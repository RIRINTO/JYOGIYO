import cx_Oracle
import mybatis_mapper2sql
import configparser


class DaoUser:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('../config.ini')
        database = config['database']['username'] + '/' + config['database']['password'] + '@' + config['database']['hostname'] + ':' + config['database']['port'] + '/' + config['database']['sid']
        self.conn = cx_Oracle.connect(database)
        self.cs = self.conn.cursor()
        self.mapper = mybatis_mapper2sql.create_mapper(xml='sample.xml')[0]

    def selectAll(self):
        pass

    def select(self):
        pass

    def insert(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass


if __name__ == '__main__':
    daoUser = DaoUser()
