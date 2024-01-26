import pandas as pd
from app.controllers.datapipeline_func.postgres_handler import get_latest_article_id, filter_latest_news

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

    
@transformer
def transform(data: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    '''
    Get latest article id and update the articles according to the article after latest article id
    '''
    try:
        latest_article_id = get_latest_article_id()
        filtered_df = filter_latest_news(data, latest_article_id)
    except (IndexError, KeyError):
        filtered_df = data

    return filtered_df[['article_id','link','title','description','pubDate','category']]


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
