from app.helpers import config_reader
import psycopg2

# Define config parameters
config = config_reader()
host = config.get('database', 'host')
port = config.get('database', 'port')
database = config.get('database', 'database')
user = config.get('database', 'user')
password = config.get('database', 'password')

def init_postgres():
    connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
    return connection