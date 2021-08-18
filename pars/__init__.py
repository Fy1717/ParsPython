from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()
UPLOAD_FOLDER = 'static/uploads/'

def createApp():
    app = Flask(__name__,
            static_url_path = '',
            static_folder = '../faces',
            template_folder = '../templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:papilon-pars@localhost:5432/papilonpars' # path should be transition to a variable
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY'] = 'papilon-secret'

    CORS(app)

    db.init_app(app)

    return app