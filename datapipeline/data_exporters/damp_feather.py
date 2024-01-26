from mage_ai.io.file import FileIO
from pandas import DataFrame

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_file(df: DataFrame, **kwargs) -> None:
    '''
    Export data to a CSV file.
    Args:
        df (DataFrame): The DataFrame to export.
        **kwargs: Additional keyword arguments.
    Returns:
        None.
    '''
    filepath = 'price.csv'
    FileIO().export(df, filepath)
