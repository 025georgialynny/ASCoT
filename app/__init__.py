from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"


def create_app(db):
    app = Flask(__name__)
    app.config["ENV"] = "development"

    secret_key = 'ascot-key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ascot:asco@localhost/flaskdb'
    app.config['SECRET_KEY'] = secret_key

    db = db.init_app(app)   
    login_manager.init_app(app)
    return app


app = create_app(db)

if app.config["ENV"] == "production":

    app.config.from_object("config_default.ProductionConfig")

elif app.config["ENV"] == "development":

    app.config.from_object("config_default.DevelopmentConfig")

else:

    app.config.from_object("config_default.ProductionConfig")



from app import views
