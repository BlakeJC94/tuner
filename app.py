import logging
import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, render_template, session

from tuner.core import tuner_match

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv(
    "SECRET_KEY", "default_fallback_key"
)  # Required to use session

app.logger.setLevel(logging.INFO)


# Define pages
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    match, shared_genres, shared_artists, recommended_artists = tuner_match(session)
    return render_template(
        "login.html",
        display_name=match["metadata"]["display_name"],
    )
