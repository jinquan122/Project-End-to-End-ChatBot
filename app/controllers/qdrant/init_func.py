import qdrant_client
import configparser
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.storage.storage_context import StorageContext

config = configparser.ConfigParser()
config.read('config.ini')

def init_qdrant(collection_name: str) -> StorageContext:
    '''
    Initiate Qdrant environment
    '''
    client = qdrant_client.QdrantClient(
        url=config.get('qdrant', 'url'), 
        api_key=config.get('qdrant', 'api_key'),
    )
    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    return storage_context