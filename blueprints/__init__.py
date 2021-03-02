from quart import flask_patch
import os
import pathlib
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from pip._vendor import cachecontrol
from quart import Quart, session, abort, redirect, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = "197119772237-jiflb55o9rad2to4dl2eboa749feittu.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

def create_app(config_class=None):
    app = Quart(__name__)
    app.config.from_object(config_class)
    initialize_extentions(app)
    register_blueprints(app)
    error_handling_functions(app)

    def login_is_required(function):
        def wrapper(*args, **kwargs):
            if "google_id" not in session:
                return abort(401)  # Authorization required
            else:
                return function()
        return wrapper

    @app.route("/login")
    async def login():
        authorization_url, state = flow.authorization_url()
        session["state"] = state
        return redirect(authorization_url)

    @app.route("/callback")
    async def callback():
        flow.fetch_token(authorization_response=request.url)

        if not session["state"] == request.args["state"]:
            abort(500)  # State does not match!

        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )

        session["google_id"] = id_info.get("sub")
        session["name"] = id_info.get("name")
        session["email"] = id_info.get("email")
        session['picture'] = id_info.get('picture')

        return redirect("/protected_area")


    @app.route("/logout")
    async def logout():
        session.clear()
        return redirect("/landing")


    @app.route("/landing")
    async def index():
        return "Hello World <a href='/login'><button>Login</button></a>"


    @app.route("/protected_area")
    @login_is_required
    async def protected_area():
        return f"Hello {session['name']}! <br/>\
            {session['google_id']} <br/>\
            {session['name']} <br/>\
            {session['email']} <br/>\
            {session['picture']} <br/><a href='/logout'><button>Logout</button></a>"

    return app.run(debug=True)

def initialize_extentions(app):
    db.init_app(app)

def register_blueprints(app):
    from blueprints.landing import landing
    app.register_blueprint(landing)

def error_handling_functions(app):
    pass