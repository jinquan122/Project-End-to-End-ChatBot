from app.controllers.agent_func.news_agent import initAgent
from flask import Response
import logging
import sys, json
from app.controllers.agent_func.evaluate import Evaluator
from traceloop.sdk import Traceloop
from app.helpers import config_reader

# Define config parameters
config = config_reader()

class AgentController:
  def __init__(self, chat_history):
    self.agent = initAgent(chat_history=chat_history)
    # Initiate Traceloop (LLM observarbility tool) for monitoring LLM performance
    Traceloop.init(disable_batch=True, api_key=config.get('traceloop','api_key'))
    
  def chat(self, msg:str, evaluate:bool = False) -> str:
      '''
      Chat with the agent.
      Args:
          msg (str): Message to be sent to the agent.
          evaluate (bool): True to activate LLM/RAG response evaluate mode.
      Returns:
          str: Response from the agent.
      '''
      if evaluate == True:
        response = self.agent.query(msg)
        evaluator = Evaluator(query=msg, response=response)
        evaluator.print_results()

      if evaluate == False:
        response = self.agent.query(msg)
      
      return response.response