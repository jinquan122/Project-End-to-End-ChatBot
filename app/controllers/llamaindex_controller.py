from app.controllers.llamaindex.agent import initArticleAgent
from flask import Response
import logging
import sys
from llama_index.llms import OpenAI, ChatMessage
from app.controllers.llamaindex.prompts import followup_template
import json
import configparser
from app.controllers.llamaindex.helpers import update_check

config = configparser.ConfigParser()
config.read('config.ini')

class LlamaIndexController:
  def __init__(self):
    self.article_agent = initArticleAgent()
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    # logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    # logging.basicConfig(filename='llama_index.log', level=logging.DEBUG)
    
  def article_chat(self, data:dict):
    msg = data.get('msg', None)
    def generate():
      # response = self.article_agent.chat(msg)
      # return str(response)
      streaming_response = self.article_agent.stream_chat(msg)
      for token in streaming_response.response_gen:
        # yield f"data: {token}\n\n" ## use for testing with Postman
        yield token
    
    if msg is not None:
        return Response(generate(), mimetype="text/event-stream")
        # return Response(generate(), mimetype="text/plain")
    else:
        # Handle the case when msg is None, e.g., return an appropriate response or raise an error.
        return Response("Invalid request: 'msg' is missing or None.", status=400, mimetype="text/plain")
  
  def resetChat(self):
    self.article_agent.reset()
    return {'msg': 'Chat cleared!'}
  
  def insert(self, data:dict)->dict:
    '''
    - Insert latest article or story data into Pinecone database.
    '''
    documents = data.get('documents', None)
    # If the data type is story, this function block is triggered for checking story data.
    if documents['type'] == 'story':
      return update_check(documents, items=["bodytext", "metadata"], metadata=["headline", "id"])

    # If the data type is article, this function block is triggered for checking article data.
    if documents['type'] == 'article':
      return update_check(documents, items=["text", "metadata"], metadata=["title", "id", "link"])
                        
  def followUpQuestions(self, data: dict) -> str:
    # TODO: instead of a separate request from the client asking
    # for follow up qustions we concatanate the response stream 
    # and push the object as a JSON string right after the response
    # finsihes
    # TODO:
    # 1. listen when the stream ends
    # follow_up_question = openai.chat(''.join(sentence))
    # questions = json.dumps(follow_up_question)
    # word = questions
    '''
    - To generate three follow up questions.

    :Params: data = dict type with answer variable inside to capture gpt answer

    - Returns a dictionary like::
    '{follow_up_questions:list[str]}'
    '''
    gpt_answer = data.get('answer', None)
    messages = [
      ChatMessage(role="system", content=followup_template),
      # ChatMessage(role="user", content=user_message),
      ChatMessage(role="system", content=gpt_answer),
    ]
    response = OpenAI().chat(messages)
    return response.message.content