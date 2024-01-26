from flask import Blueprint, request
from app.controllers.agent_controller import AgentController

agentController = AgentController()

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/chat", methods=['POST'])
def llamaIndexArticleChatHandler():
  return agentController.chat(request.json)