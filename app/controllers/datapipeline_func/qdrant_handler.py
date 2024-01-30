from llama_index import (
    VectorStoreIndex,
    ServiceContext,
    Document,
)
from llama_index.node_parser import SentenceSplitter
from llama_index.embeddings import HuggingFaceEmbedding
import openai
from pandas import DataFrame
from app.controllers.qdrant.init_func import init_qdrant
from app.helpers import config_reader

# Define config parameters
config = config_reader()
openai_api_key = config.get('openai', 'api_key')

openai.api_key = openai_api_key
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

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
    node_parser = SentenceSplitter.from_defaults(
        chunk_size=1024,
        chunk_overlap=20
    )
    service_context = ServiceContext.from_defaults(
        embed_model = embed_model,
        node_parser = node_parser
        )
    index = VectorStoreIndex.from_documents(
        docs, 
        storage_context = storage_context,
        service_context = service_context
    )