import logging
import os
from dataclasses import asdict

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


@app.route("/results")
def results():
    if "match" in session:
        (
            match,
            shared_genres,
            shared_artists,
            recommended_artists,
        ) = (
            session["match"],
            session["shared_genres"],
            session["shared_artists"],
            session["recommended_artists"],
        )
    else:
        output = tuner_match(session)

        (
            session["match"],
            session["shared_genres"],
            session["shared_artists"],
            session["recommended_artists"],
        ) = (
            asdict(output.match_md),
            output.shared_genres,
            output.shared_artists,
            output.recommended_artists,
        )

    return render_template(
        "results.html",
        match={
            "name": session["match"]["metadata"]["display_name"],
            "score": session["match"]["score"],
            "profile_link": session["match"]["metadata"]["url"],
            "common_genres": session["shared_genres"],
            "common_artists": session["shared_artists"],
            "recommended_artists": session["recommended_artists"],
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
