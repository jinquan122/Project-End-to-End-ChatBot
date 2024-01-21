from llama_index import get_response_synthesizer
from llama_index.tools import QueryEngineTool, FunctionTool, ToolMetadata
from llama_index.llms import OpenAI
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.agent import OpenAIAgent
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from app.controllers.llamaindex.prompts import text_qa_template, refine_template, system_prompt
import requests
import configparser
from llama_index.postprocessor import SimilarityPostprocessor
from llama_index.postprocessor import MetadataReplacementPostProcessor

config = configparser.ConfigParser()
config.read('config.ini')

openai_api_key = config.get('openai', 'api_key')
pinecone_api_key = config.get('pinecone', 'article_api_key')
pinecone_environment = config.get('pinecone', 'article_environment')

fcd_token = config.get('fcd', 'token')
hostUrl = "https://fcdbackendapiproduction.azurewebsites.net"

# def latest_news():
#   # response = requests.get(f"http://127.0.0.1:3000/sec/stories/top/0/25?token={fcd_token}").json()
#   response = requests.get(f"https://fcdbackendapiproduction.azurewebsites.net/sec/stories/top/0/25?token={fcd_token}").json()
#   data = response.get("data")
#   linkList = [f'<a href="https://www.aperio-fcd.com/story/{d.get("id")}" target="_blank">{d.get("headline")}</a>' for d in data.get("results")][:10]
#   return "Here are the latest news headlines rendered server side. When someone asks you about the latest news return the list preserving the HTML markup because the client is expecting it:\n- " + "\n - ".join(linkList)

def get_latest_articles():
  url = f"{hostUrl}/sec/news-feed/articles/filter/0/2?token={fcd_token}"
  payload = {
    "filters": {
      "startDate": "2024-01-08",
      "score": "0.6"
    }
  }

  response = requests.post(url, data=payload).json()
  data = response.get("data")
  titles = [d.get("title") for d in data.get("results")]
  return "Here are the latest article headlines:\n\n- " + "\n - ".join(titles)
  
# latest_news_tool = FunctionTool.from_defaults(
#   fn=latest_news,
#   name="latest_news",
#   description="Get the latest news headlines.",
# )

latest_articles_tool = FunctionTool.from_defaults(
  fn=get_latest_articles,
  name="latest_articles",
  description="Get the latest articles headlines.",
)

# def initAgent(index):
#   retriever = VectorIndexRetriever(
#     index=index, 
#     similarity_top_k=3,
#   )
#   response_synthesizer = get_response_synthesizer(
#     response_mode="compact",
#     text_qa_template=text_qa_template,
#     refine_template=refine_template,
#   )
#   vector_db_query_engine = RetrieverQueryEngine(
#     retriever=retriever,
#     response_synthesizer=response_synthesizer,
#   )
#   vector_query_engine_tool = QueryEngineTool(
#     query_engine=vector_db_query_engine,
#     metadata=ToolMetadata(
#       name="news_database",
#       description="Get news articles and information about political entities and events. Use a detailed plain text question as input to the tool.",
#     )
#   )
#   return OpenAIAgent.from_tools(
#     [latest_news_tool, vector_query_engine_tool],
#     llm=OpenAI(model="gpt-3.5-turbo-1106"),
#     verbose=True,
#     system_prompt="You must preserve any HTML markup in the output of function calls.",
#   )

import openai
import pinecone
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index import ServiceContext
from llama_index.vector_stores import PineconeVectorStore
from llama_index import VectorStoreIndex

def initArticleAgent():
  '''
  - articleAgent is an agent which read the latest news feed that are scrapped from websites.
  '''
  openai.api_key = openai_api_key
  pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
  embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
  service_context = ServiceContext.from_defaults(embed_model = embed_model)
  article_vector_store = PineconeVectorStore(pinecone_index=pinecone.Index("article-index"))
  article_index = VectorStoreIndex.from_vector_store(
    vector_store=article_vector_store, 
    service_context=service_context
    )
  retriever = VectorIndexRetriever(
    index=article_index,
    similarity_top_k=10
  )
  node_postprocessors = [
        SimilarityPostprocessor(similarity_cutoff=0.5),
        MetadataReplacementPostProcessor(target_metadata_key="window"),
        # KeywordNodePostprocessor(
        # required_keywords=["news"],
        # exclude_keywords=["playground"])
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
      name="article_database",
      description="Get articles and information about political entities and events.",
    )
  )
  return OpenAIAgent.from_tools(
    [latest_articles_tool, vector_query_engine_tool],
    llm=OpenAI(model="gpt-3.5-turbo-1106"),
    verbose=True,
    system_prompt=system_prompt,
    temperature=0,
    seed=1234
  )
