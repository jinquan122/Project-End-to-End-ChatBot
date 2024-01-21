import pinecone
import configparser
import pandas as pd
from llama_index.vector_stores import PineconeVectorStore
from llama_index import StorageContext ,ServiceContext, Document, VectorStoreIndex
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.node_parser import SentenceWindowNodeParser
import json
import datetime
import re
from typing import Callable, List
from nltk.tokenize import sent_tokenize
import os
from app.helpers import write_path, read_path, get_time

config = configparser.ConfigParser()
config.read('config.ini')

def remove_html(text:str)->str:
  '''
  - To perform preprocessing on bodytext by removing html sign.
  '''
  pattern = re.compile(r'<.*?>')
  cleaned_text = re.sub(pattern, '', text)
  cleaned_text = cleaned_text.replace('  ',' ')
  return cleaned_text

def not_relevant_pattern(sentence):
  '''
  - Define email and phone pattern using regex method.
  '''
  email_pattern = r'\S+@\S+'
  phone_pattern = r'\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4}'
  return re.search(email_pattern, sentence) or re.search(phone_pattern, sentence)

def data_preprocessing(text: str):
  '''
  - Perform data preprocessing steps. The pattern include:
  1. Delete '\xa0'
  2. Delete all special character except punctuations
  3. Delete all URLs.
  4. Delete '\u202f'
  5. Delete '\'
  6. Adjust double spacing to single spacing
  '''
  cleaned_text = text.replace('\xa0',' ') 
  cleaned_text = re.sub(r'[^a-zA-Z0-9.,;:?!\'"\s-]', ' ', cleaned_text)
  cleaned_text = re.sub(r'https?://\S+|www\.\S+', '', cleaned_text)
  cleaned_text = re.sub(r'\u202f', ' ', cleaned_text) 
  cleaned_text = re.sub(r'\\', '', cleaned_text) 
  cleaned_text = re.sub(r'  ', ' ', cleaned_text)
  return cleaned_text

def filter_sentence(sentences: list[str]) -> list[str]:
  '''
  - Perform sentence filtering while spliting the text into sentences. This function will 
  make use of not_relevant_pattern function to exclude email and phone sentences. Next,
  There are a list of phrases defined to exclude the sentences. Lastly, all sentences will be more than 10 words.
  '''
  phrases_to_remove = [
  "reporting by",
  "editing by",
  "further information",
  "more information",
  "click",
  "please contact",
  ]
  filtered_sentences = [sentence for sentence in sentences if not not_relevant_pattern(sentence)] 
  for phrase in phrases_to_remove:
    filtered_sentences = [sentence for sentence in filtered_sentences if phrase not in sentence.lower()]
  sentences_clean = [ sent for sent in filtered_sentences if len(sent)> 25] # Make sure all the sentences are more than 10 words #TODO: Check if 25 characters works better
  return sentences_clean

def sentence_split_custom_function() -> Callable[[str], List[str]]:
  def split(text: str) -> List[str]:
    final_sentences = []
    sents = re.split(r'\n|\t', text)
    for j in sents:
      sentences = sent_tokenize(j)
      for sent in sentences:
        final_sentences.append(sent)
    processed_sentences = filter_sentence(final_sentences)
    final_processed_sentences = []
    for sent in processed_sentences:
      final_processed_sentences.append(data_preprocessing(sent))
    return final_processed_sentences
  return split

def count_char(text: str) -> int:
  cnt = len(text)
  return cnt
   
def outlier_record(article_id_list: list, 
                   outlier_file_path: str = "outlier.json") -> None:
  '''
  - Record outlier text which are more than 2000- characters into a JSON file called outlier.json.
  '''
  outlier_num = len(article_id_list)
  transformed_list = [{"id": i} for i in article_id_list]
  if os.path.exists(outlier_file_path): # Check if the JSON file exists
      data = read_path(outlier_file_path)
      data.extend(transformed_list)
      write_path(outlier_file_path, data)
      print(f"Outlier data has been successfully updated in {outlier_file_path}. There are {outlier_num} outliers.")
  else:
      # If it doesn't exist, create a new file with the specified format
      write_path(transformed_list)
      print(f"New file {outlier_file_path} created. There are {outlier_num} outliers.")

def db_update(documents: dict,
              target_db: str,
              character_length_filter: int = 20000) -> dict: 
  '''
  - To update Pinecone vector database with latest articles and stories.

  :Params:  documents = JSON object in the following format:
                        {"documents":{
                          "items": [
                              {"text": "example", "metadata": {"title": 1, "id": 1, "link": 1}},
                              {"text": "example2", "metadata": {"title": 2, "id": 2, "link": 2}}
                          ],
                          "type": "article"
                      }}
            target_db = pinecone database

  Steps:
  1. Initiate pinecone environment.
  2. Choose target db: either 'article' or 'story'.
  3. Store the json data from API call in Pandas dataframe.
  4. Perform preprocessing for uploading to Pinecone vector database.
     'article' mode: documents will be first splited into sentences format for detailed searching.
     'story' mode: documents will stored in the whole article format.
  5. Upload latest 100 objects with latest article_id as filter.

  Output: Message type - stating the time for completing the upload action.
  '''
  # Define local embedding model
  embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
  index_name = f'{target_db}-index'
  docs = []
  
  if target_db == "article":
    # Initiate Pinecone environment
    pinecone.init(api_key = config.get('pinecone', 'article_api_key'), environment = config.get('pinecone', 'article_environment'))
    pinecone_index = pinecone.Index(index_name)
    vector_store = PineconeVectorStore(
        pinecone_index = pinecone_index,
        add_sparse_vector = False,
    )
    storage_context = StorageContext.from_defaults(vector_store = vector_store)
    # Store the json data in Pandas dataframe.
    df = pd.DataFrame(documents)
    df['cnt'] = df['text'].apply(lambda x:count_char(x))
    outlier_df = df[df['text'].apply(len) > character_length_filter]
    outlier_article_list = [item['id'] for item in outlier_df['metadata']]
    # TODO: Detect empty outlier , greater > 0, continue function
    if len(outlier_df) > 0: 
      outlier_record(outlier_article_list) 
    valid_article_df = df[df['text'].apply(len) <= character_length_filter] 
    # TODO: Detect empty valid_article_df , greater > 0, continue function
    if len(valid_article_df) > 0: 
      valid_article_df = valid_article_df.reset_index()
      # Perform preprocessing for uploading to Pinecone vector database.
      for i, row in valid_article_df.iterrows():
          docs.append(Document(
              text = row['text'],
              metadata = {
                          'headline':row['metadata']['title'],
                          'id': row['metadata']['id'],
                          'link': row['metadata']['link']}
                          ))
      node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=1,  # control how many sentences on either side to capture
        window_metadata_key="window",
        original_text_metadata_key="original_sentence",
        sentence_splitter=sentence_split_custom_function()
        )
      service_context = ServiceContext.from_defaults(
          embed_model = embed_model,
          node_parser = node_parser)
      index = VectorStoreIndex.from_documents(
        docs, 
        storage_context = storage_context,
        service_context = service_context
        )
    
  elif target_db == "story":
    # Initiate Pinecone environment
    pinecone.init(api_key = config.get('pinecone', 'story_api_key'), environment = config.get('pinecone', 'story_environment'))
    pinecone_index = pinecone.Index(index_name)
    vector_store = PineconeVectorStore(
        pinecone_index = pinecone_index,
        add_sparse_vector = False,
    )
    storage_context = StorageContext.from_defaults(vector_store = vector_store)
    # Store the json data in Pandas dataframe.
    df = pd.DataFrame(documents)
    # Perform preprocessing by removing html sign
    df['bodytext'] = df['bodytext'].apply(lambda x:remove_html(x))
    # Perform preprocessing for uploading to Pinecone vector database.
    for i, row in df.iterrows():
        docs.append(Document(
            text = row['bodytext'],
            metadata = {
                        'headline':row['metadata']['headline'],
                        'id': row['metadata']['id']}
                        ))
    service_context = ServiceContext.from_defaults(embed_model = embed_model)
    index = VectorStoreIndex.from_documents(
        docs, 
        storage_context = storage_context,
        service_context = service_context
        )
  # Record current time
  time = get_time()

  try:
    row_num = len(df)
    return {'msg':"Time: {} - Pinecone {} database update completed with {} rows inserted!".format(time, target_db, row_num), 'error_list': None}
  
  except (KeyError, ValueError):
     return {'msg':"Time: {} - No additional data were updated to database as Pinecone {} database is updated.".format(time, target_db), 'error_list': None}
  
def _reset_pinecone_db():
  # Don't call this function, this will lead to loss of database!!!
  # The purpose of the function is to record the parameters needed to create Pinecone index.
  pinecone.init(api_key = config.get('pinecone', 'story_api_key'), environment = config.get('pinecone', 'story_environment'))
  pinecone.delete_index('story-index')
  pinecone.create_index("story-index", dimension=384, metric="cosine", pods=1, pod_type="s1.x1")