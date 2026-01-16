from flask import Flask
from dotenv import load_dotenv
import os
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

from helpers.database import db
from resources.Usuarios import usuarios_bp

load_dotenv()

app = Flask(__name__)

# Configurações
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Extensões
db.init_app(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

# Blueprints
app.register_blueprint(usuarios_bp)
