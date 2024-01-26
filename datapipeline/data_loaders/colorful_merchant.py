import pandas as pd
import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_api(*args, **kwargs) -> pd.DataFrame:
    """
    Template for loading data from API
    """
    url = config.get('financialmodelingprep', 'url')
    response = requests.get(url)
    price = [item['close'] for item in response.json()['historical']]
    date = [item['date'] for item in response.json()['historical']]
    
    return pd.DataFrame({'date': date, 'price': price})


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
