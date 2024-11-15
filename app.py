import logging
import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, render_template, session

from tuner.globals import SCOPE

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_fallback_key')  # Required to use session

app.logger.setLevel(logging.INFO)


# Define pages
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=SCOPE,
            show_dialog=True,
            cache_handler=FlaskSessionCacheHandler(session),
        ),
    )
    user = sp.current_user()

    return render_template("login.html", display_name=user['display_name'])

