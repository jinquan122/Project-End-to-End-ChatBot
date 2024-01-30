from llama_index import get_response_synthesizer
from llama_index.tools import QueryEngineTool, FunctionTool, ToolMetadata
from llama_index.llms import OpenAI
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.postprocessor import SimilarityPostprocessor, MetadataReplacementPostProcessor, TimeWeightedPostprocessor
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index import ServiceContext, VectorStoreIndex
from app.controllers.agent_func.prompts import text_qa_template, refine_template, system_prompt
from app.controllers.qdrant.init_func import init_qdrant
import configparser
from llama_index.agent import OpenAIAgent
import openai
from app.helpers import config_reader
from app.controllers.agent_func.agent_tool.google_search import GoogleSearch
from app.controllers.agent_func.agent_tool.graph_plotting import plotting_tool
from app.controllers.agent_func.agent_tool.recent_news import latest_news_tool

# Define config parameters
config = config_reader()
openai_api_key = config.get('openai', 'api_key')

openai.api_key = openai_api_key
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

def initAgent(
    model = 'gpt-3.5-turbo-1106',
    temperature: int = 0,
    seed: int = 1234,
    similarity_cutoff: int = 0.5,
    retrieve_top_k: int = 10
) -> OpenAIAgent:
  '''
  Initialize the agent with three tools.
  1. Vector db retriever tool
  2. Google Search tool
  3. Plotting tool

  Args:
    model (str): The model to use for the agent.
    temperature (int): The temperature to use for the agent.
    seed (int): The seed to use for the agent.
    similarity_cutoff (int): The similarity cutoff to use for the agent.
    retrieve_top_k (int): The retrieve top k to use for the agent.

  Returns:
    OpenAIAgent: The agent with three tools.
  '''
  # Define vector db retriever tools
  storage_context = init_qdrant('article-news') 
  service_context = ServiceContext.from_defaults(embed_model = embed_model)
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
        MetadataReplacementPostProcessor(target_metadata_key="window"),
        TimeWeightedPostprocessor(time_decay=0.5, time_access_refresh=False, top_k=10)
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
      description="Get news article.",
    )
  )

  # Define Google Search tool
  gsearch = GoogleSearch()
  gsearch_tools, gsearch_load_and_search_tools = gsearch.stack()

  # Define plotting tool
  plotting_tool

  # Define latest news tool
  latest_news_tool

  return OpenAIAgent.from_tools(
    [vector_query_engine_tool, *gsearch_tools[1::], *gsearch_load_and_search_tools, plotting_tool, latest_news_tool],
    llm=OpenAI(model=model),
    verbose=True,
    system_prompt=system_prompt,
    temperature=temperature,
    seed=seed
  )