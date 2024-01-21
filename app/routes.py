from flask import Blueprint, request
from app.controllers.llamaindex_controller import LlamaIndexController

llamaIndexController = LlamaIndexController()

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/llama-index-insert", methods=['POST'])
def llamaIndexInsertHandler():
  return llamaIndexController.insert(request.json)

@api_blueprint.route("/llama-follow-up-questions", methods=['POST'])
def llamaIndexFollowUpHandler():
  return llamaIndexController.followUpQuestions(request.json)

@api_blueprint.route("/llama-article-chat", methods=['POST'])
def llamaIndexArticleChatHandler():
  return llamaIndexController.article_chat(request.json)