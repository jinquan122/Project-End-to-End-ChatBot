import psycopg2
import pandas as pd
from app.controllers.postgres.init_func import init_postgres
from llama_index.tools import FunctionTool

def get_latest_news():
    # Establish a connection to the PostgreSQL database
    try:
        connection = init_postgres()
        # Example: Execute another query
        query = "SELECT * FROM news ORDER BY pubdate DESC LIMIT 10;"
        df = pd.read_sql_query(query, connection)
    except psycopg2.Error as e:
        print("Error: Unable to connect to the database.")
        print(e)
    finally:
        if connection:
            connection.close()  
    return df

latest_news_tool = FunctionTool.from_defaults(
    fn=get_latest_news, 
    name='latest_news', 
    description='Get recent and latest news article only. Use this function when user ask for recent or latest news only!')