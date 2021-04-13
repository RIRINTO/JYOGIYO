import configparser

config = configparser.ConfigParser()
config['database'] = {'type': 'oracle',
                      'hostname': 'ririnto.asuscomm.com',
                      'port': '1521',
                      'sid': 'xe',
                      'username': 'team4',
                      'password': 'java'}
config['DIR_UPLOAD'] = {'DIR_UPLOAD': "W:/uploads"}
config['Kakao'] = {'KakaoAK': '47c87e7944c1f57028905bf3ca39502b'}
config['network'] = {'HOST':'0.0.0.0',
                     'PORT':5004}
with open('config.ini', 'w') as configfile:
    config.write(configfile)
