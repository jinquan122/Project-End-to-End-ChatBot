from app.controllers.datapipeline_func.postgres_handler import remove_single_quotes
import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



@transformer
def transform(data: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    '''
    Perform data preprocessing. Remove single quotes from columns: article_id, link, description, category. 
    
    Args:
        data (pd.DataFrame): Data to preprocess.
    Returns:
        pd.DataFrame: Preprocessed data.
    '''
    column_list = ['article_id', 'link', 'description', 'category']
    for i in column_list:
        column = i
        data[column] = data[column].apply(lambda x: remove_single_quotes(str(x)))

    return data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
