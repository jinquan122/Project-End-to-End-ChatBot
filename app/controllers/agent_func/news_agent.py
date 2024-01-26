from llama_index import get_response_synthesizer
from llama_index.tools import QueryEngineTool, FunctionTool, ToolMetadata
from llama_index.llms import OpenAI
from llama_index.agent import OpenAIAgent
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.postprocessor import SimilarityPostprocessor, MetadataReplacementPostProcessor
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index import ServiceContext, VectorStoreIndex
from app.controllers.agent_func.prompts import text_qa_template, refine_template, system_prompt
from app.controllers.qdrant.init_func import init_qdrant
import configparser
import openai

config = configparser.ConfigParser()
config.read('config.ini')

openai_api_key = config.get('openai', 'api_key')

def initAgent(
    model: str = "gpt-3.5-turbo-1106",
    temperature: int = 0,
    seed: int = 1234,
    similarity_cutoff: int = 0.5,
    retrieve_top_k: int = 10
):
  '''
  Initialize the agent with the vector database.
  Returns:
    OpenAIAgent: The agent with the vector database.
  '''
  openai.api_key = openai_api_key
  embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
  service_context = ServiceContext.from_defaults(embed_model = embed_model)
  # Connect to Qdrant vector database.
  storage_context = init_qdrant('article-news') 
  index = VectorStoreIndex.from_vector_store(
    vector_store=storage_context.vector_store,
    service_context=service_context
    )
  retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=retrieve_top_k
  )
  node_postprocessors = [
        SimilarityPostprocessor(similarity_cutoff=similarity_cutoff),
        MetadataReplacementPostProcessor(target_metadata_key="window")
    ]
  response_synthesizer = get_response_synthesizer(
    response_mode="compact",
    text_qa_template=text_qa_template,
    # refine_template=refine_template
  )
  vector_db_query_engine = RetrieverQueryEngine(
    retriever=retriever,
    node_postprocessors=node_postprocessors,
    response_synthesizer=response_synthesizer
  )
  vector_query_engine_tool = QueryEngineTool(
    query_engine=vector_db_query_engine,
    metadata=ToolMetadata(
      name="database",
      description="Get Apple related news article.",
    )
  )
  return OpenAIAgent.from_tools(
    [vector_query_engine_tool],
    llm=OpenAI(model=model),
    verbose=True,
    system_prompt=system_prompt,
    temperature=temperature,
    seed=seed
  )
