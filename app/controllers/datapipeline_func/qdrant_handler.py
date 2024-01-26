from llama_index import (
    VectorStoreIndex,
    ServiceContext,
    Document,
)
from llama_index.node_parser import SentenceWindowNodeParser
from llama_index.embeddings import HuggingFaceEmbedding
import configparser
import openai
from pandas import DataFrame
from app.controllers.qdrant.init_func import init_qdrant

config = configparser.ConfigParser()
config.read('config.ini')

openai_api_key = config.get('openai', 'api_key')
openai.api_key = openai_api_key

def load_qdrant(df: DataFrame, collection_name:str) -> None:
    '''
    Connect to Qdrant vector database and upload the dataframe to it.
    Args:
        df (DataFrame): Dataframe containing the data to be uploaded to the database.
        collection_name (str): Name of the collection to be connected.
    Returns:
        None.
    '''
    docs = []
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    storage_context = init_qdrant(collection_name) # Connect to Qdrant vector database.
    # Perform data preprocessing for uploading to Qdrant vector database.
    for i, row in df.iterrows():
        docs.append(Document(
            text = row['description'],
            metadata = {
                        'title':row['title'],
                        'id': row['article_id'],
                        'link': row['link'],
                        'date': row['pubDate'],
                        'category': row['category']}
                        ))
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=2,  # control how many sentences on either side to capture
        window_metadata_key="window",
        original_text_metadata_key="original_sentence"
    )
    service_context = ServiceContext.from_defaults(
        embed_model = embed_model,
        node_parser = node_parser)
    index = VectorStoreIndex.from_documents(
        docs, 
        storage_context = storage_context,
        service_context = service_context
    )