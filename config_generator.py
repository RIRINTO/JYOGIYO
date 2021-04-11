import configparser

config = configparser.ConfigParser()
config['database'] = {'type': 'oracle',
                      'hostname': 'ririnto.asuscomm.com',
                      'port': '1521',
                      'sid': 'xe',
                      'username': 'team4',
                      'password': 'java'}
with open('config.ini', 'w') as configfile:
    config.write(configfile)
