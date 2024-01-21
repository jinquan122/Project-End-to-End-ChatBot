from flask import Flask
from flask_cors import CORS
from app.routes import api_blueprint

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(api_blueprint, url_prefix='/api')