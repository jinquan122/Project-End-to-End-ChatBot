from pandas import DataFrame
from app.controllers.datapipeline_func.qdrant_handler import load_qdrant

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data(df: DataFrame) -> None:
    '''
    Load the data into the Qdrant database.
    Args:
        df (DataFrame): The DataFrame to load.
    Returns:
        None.
    '''
    load_qdrant(df, collection_name="article-news")
    


