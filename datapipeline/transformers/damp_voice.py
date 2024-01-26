import pandas as pd
import os

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    '''
    Store data in price.csv file. If price.csv exists, read the csv file with pandas. Extract the latest date and update the date after.
    If price.csv does not exist, create a new csv file with the data.
    Return the updated dataframe.
    '''
    # To find if price.csv exists, if yes, read the csv file with pandas. Extract the latest date and update the date after.
    if os.path.exists('price.csv'):
        db_df = pd.read_csv('price.csv')
        # To convert date column to date format so that can get the latest date
        db_df['date'] = pd.to_datetime(db_df['date'])
        df['date'] = pd.to_datetime(df['date'])
        # To get the latest date and filter those before latest date
        latest_date = db_df['date'].max()
        df = df[df['date'] > latest_date]
        # To update df to db_df
        updated_df = pd.concat([db_df, df])
    else:
        updated_df = df

    return updated_df.reset_index(drop=True)


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
