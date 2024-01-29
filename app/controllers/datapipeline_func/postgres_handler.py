import psycopg2
import pandas as pd
from app.helpers import config_reader

# Define config parameters
config = config_reader()
host = config.get('database', 'host')
port = config.get('database', 'port')
database = config.get('database', 'database')
user = config.get('database', 'user')
password = config.get('database', 'password')

def get_latest_article_id():
    # Establish a connection to the PostgreSQL database
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        # Example: Execute another query
        query = "SELECT * FROM news ORDER BY pubdate DESC LIMIT 1;"
        df = pd.read_sql_query(query, connection)
    except psycopg2.Error as e:
        print("Error: Unable to connect to the database.")
        print(e)
    finally:
        if connection:
            connection.close()
    return df['article_id'][0]

def filter_latest_news(df, latest_article_id):
    ind = df.loc[df['article_id'] == latest_article_id].index[0]
    filtered_df = df.iloc[:ind]
    return filtered_df

def remove_single_quotes(s):
    return s.replace("'", "")