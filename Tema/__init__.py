from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from os.path import join, dirname, realpath
from flask import Flask, redirect, url_for, render_template
from flask_dance.contrib.github import make_github_blueprint, github


import eventlet
eventlet.monkey_patch()

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'R\x1a^-\x14?mq\x1ce\xf7\xefi\xb7\x0e\xa0\x02\x0c\xd6-$\x033\xc4'
app.config['IMAGE_UPLOADS'] = join(dirname(realpath(__file__)), 'static/imgs/')
app.config['FILE_UPLOADS'] = join(dirname(realpath(__file__)), 'static/submissions/')
app.config['UPLOAD_FOLDER'] = join(dirname(realpath(__file__)), 'static/upload_user')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite3'
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# modules import
from Tema.routes import *
from Tema.models import User
from Tema.network import *

with app.app_context():
    db.create_all()
