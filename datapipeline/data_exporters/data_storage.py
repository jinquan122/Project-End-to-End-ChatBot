from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import Postgres
from pandas import DataFrame
from os import path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_postgres(df: DataFrame, **kwargs) -> None:
    '''
    Export data to a PostgreSQL table.
    Args:
        df (DataFrame): The DataFrame to export.
        **kwargs: Additional keyword arguments.
    Returns:
        None.
    '''
    table_name = 'news'  
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'

    with Postgres.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
        loader.export(
            df,
            table_name = table_name,
            index=False,  
            if_exists='update', 
        )