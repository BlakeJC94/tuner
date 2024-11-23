import logging
import os

from dotenv import load_dotenv
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
        match={
            "name": match["metadata"]["display_name"],
            "score": match["score"],
            "profile_link": match["metadata"]["url"],
            "common_genres": shared_genres,
            "common_artists": shared_artists,
            "recommended_artists": recommended_artists,
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
