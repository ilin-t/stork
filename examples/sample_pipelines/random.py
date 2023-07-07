from configparser import ConfigParser

random_path = "this is a string"

print(random_path)

parser = ConfigParser()
parser.read("../db_conn/config_db.ini")

db_config={}
if parser.has_section('psycopg2'):
    params = parser.items('psycopg2')
    for param in params:
        db_config[param[0]] = param[1]

else:
    raise Exception('Section {0} not found in the {1} file'.format('psycopg2', 'config_db.ini'))

