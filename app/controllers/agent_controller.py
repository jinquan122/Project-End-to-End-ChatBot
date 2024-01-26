from app.controllers.agent_func.news_agent import initAgent
from flask import Response

class AgentController:
  def __init__(self):
    self.agent = initAgent()
    
  def chat(self, msg:str):
    # msg = data.get('msg', None)
    # def generate():
      response = self.agent.chat(msg)
      return response.response
      # streaming_response = self.agent.stream_chat(msg)
      # for token in streaming_response.response_gen:
        # yield f"data: {token}\n\n" ## use for testing with Postman
        # yield token
    
    # if msg is not None:
    #     # return Response(generate(), mimetype="text/event-stream")
    #     return Response(generate(), mimetype="text/plain")
    # else:
    #     # Handle the case when msg is None, e.g., return an appropriate response or raise an error.
    #     return Response("Invalid request: 'msg' is missing or None.", status=400, mimetype="text/plain")