# import pyrebase
# from flask import *
# from oauth2client.contrib.flask_util import UserOAuth2
#
# config = {
#     "apiKey": "AIzaSyDmn0dJl4lvTASIPtPD5vfHIoG6IIWg5dc",
#     "authDomain": "travel-b97bd.firebaseapp.com",
#     "databaseURL": "https://travel-b97bd.firebaseio.com",
#     "projectId": "travel-b97bd",
#     "storageBucket": "travel-b97bd.appspot.com",
#     "messagingSenderId": "850989183342",
#     "appId": "1:850989183342:web:6eb717f390c612c8"
# }
#
# app = Flask(__name__)
# firebase = pyrebase.initialize_app(config)
# db = firebase.database()
# auth = firebase.auth()
# app.config['SECRET_KEY'] = 'AIzaSyDrpj7_GwCxq2krshdqkainpdlFvLl9WNI'
# app.config['GOOGLE_OAUTH2_CLIENT_ID'] = '850989183342-i3f30kop5phf368pbmaajas6ii9i3v1b.apps.googleusercontent.com'
# app.config['GOOGLE_OAUTH2_CLIENT_SECRET'] = 'W4k_wh73Su4uTgRpyVqKUtL1'
#
# oauth2 = UserOAuth2(app)
#
# @app.route('/info')
# @oauth2.required
# def info():
#     return "Hello, {} ({})".format(oauth2.email, oauth2.user_id)
#
#
# @app.route('/optional')
# def optional():
#     if oauth2.has_credentials():
#         return '로그인!'
#     else:
#         return '로그인 하세여!'
#
#
# @app.route("/")
# @app.route("/login", methods=['POST'])
# def Login():
#     unsuccessful = 'Please check your credentials'
#     successful = 'Login successful'
#     if request.method == 'POST':
#         try:
#             return render_template('Main.html', s=successful)
#         except:
#             return render_template('Login.html', us=unsuccessful)
#     return render_template(
#                 'Login.html',
#                 title="Travel",
#             )
#
# @app.route("/Main", methods=['GET', 'POST'])
# @oauth2.required
# def Main():
#     id = request.form['id']
#     return render_template('Main.html', id=id)

import os
import json
import datetime

from flask import Flask, url_for, redirect, \
    render_template, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, \
    logout_user, current_user, UserMixin
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError

basedir = os.path.abspath(os.path.dirname(__file__))
os.environ['DEBUG'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

"""App Configuration"""


class Auth:
    """Google Project Credentials"""
    CLIENT_ID = ('850989183342-i3f30kop5phf368pbmaajas6ii9i3v1b.apps.googleusercontent.com')
    CLIENT_SECRET = 'W4k_wh73Su4uTgRpyVqKUtL1'
    REDIRECT_URI = 'http://localhost:5000/oauth2authorize'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    RESPONSE_URI = 'http://localhost:5000/oauth2callback'
    SCOPE = ['profile', 'email']


class Config:
    """Base config"""
    APP_NAME = "Test Google Login"
    SECRET_KEY = "AIzaSyDrpj7_GwCxq2krshdqkainpdlFvLl9WNI"


class DevConfig(Config):
    """Dev config"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "test.db")


class ProdConfig(Config):
    """Production config"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "prod.db")


config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}

"""APP creation and configuration"""
app = Flask(__name__)
app.config.from_object(config['dev'])
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

""" DB Models """


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
""" OAuth Session creation """


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth


@app.route('/')
@login_required
def index():
    return render_template('main.html')


@app.route('/login')
def login():
    logout_user()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)


@app.route('/oauth2authorize')
def callback():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(Auth.TOKEN_URI, client_secret=Auth.CLIENT_SECRET,
                                    code = "/oauth2callback",
                                    authorization_response = Auth.REDIRECT_URI)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email)
            if user is None:
                user = User()
                user.email = email
            user.name = user_data['name']
            print(token)
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/main')
@login_required
def main():
    return render_template('login.html', auth_url=auth_url)


@app.after_request
def set_response_headers(response):
	response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '0'
	return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
# -> main.html
