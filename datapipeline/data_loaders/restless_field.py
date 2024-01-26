import pandas as pd
from newsdataapi import NewsDataApiClient
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

api = NewsDataApiClient(apikey=config.get('newsdataapi','api_key'))

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_api(*args, **kwargs) -> pd.DataFrame:
    """
    Template for loading data from API
    """
    response = api.news_api(q= "Apple" , 
                            country = "us", 
                            language = "en", 
                            category = ["business", "politics", "technology", "world", "crime"])

    return pd.DataFrame(response['results'])


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
