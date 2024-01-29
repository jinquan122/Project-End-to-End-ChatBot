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
  def __init__(self):
    self.agent = initAgent()
    Traceloop.init(disable_batch=True, api_key=config.get('traceloop','api_key'))
    
  def chat(self, msg:str, evaluate:bool = False) -> str:
      # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
      # logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
      if evaluate == True:
        response = self.agent.query(msg)
        self.evaluator = Evaluator(msg, response)
        faith_passing, faith_score, faith_feedback = self.evaluator.faithfulness_evaluator()
        context_passing, context_score, context_feedback = self.evaluator.context_evaluator()
        relevancy_passing, relevancy_score, relevancy_feedback = self.evaluator.relevancy_evaluator()
        # guideline_results = self.evaluator.guideline_evaluator()
        print("Faithfulness: ", faith_passing,faith_score,faith_feedback)
        print("Context: ", context_passing,context_score,context_feedback)
        print("Relevancy: ", relevancy_passing,relevancy_score,relevancy_feedback)
        # for guideline_result in guideline_results:
        #   guideline = guideline_result['guideline']
        #   result = guideline_result['eval_result']
        #   print("Guideline: ",guideline,result.passing,result.score,result.feedback)

      if evaluate == False:
        response = self.agent.query(msg)
      
      return response.response