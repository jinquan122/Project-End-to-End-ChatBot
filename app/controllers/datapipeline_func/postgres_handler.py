import psycopg2
import pandas as pd
from app.controllers.postgres.init_func import init_postgres

def get_latest_article_id():
    # Establish a connection to the PostgreSQL database
    try:
        connection = init_postgres()
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