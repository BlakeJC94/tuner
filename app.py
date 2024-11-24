import logging
import os
import random
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
    if not "result" in session:
        output = tuner_match(session)

        image_urls = [u for u in output.image_urls if u]
        image_urls = random.sample(image_urls, min(6, len(image_urls)))

        tracks = []
        for r in output.tracks:
            imgs = r["album"]["images"]
            img_url = next((i["url"] for i in imgs if i["width"] == 64), None)
            if img_url is None:
                continue
            tracks.append(
                {
                    "name": r["name"],
                    "album": r["album"]["name"],
                    "artists": ", ".join([a["name"] for a in r["artists"]]),
                    "image_url": img_url,
                }
            )

        session["result"] = {
            "name": output.match_md.display_name,
            "score": f"{100 * output.score:.2f}",
            "profile_link": output.match_md.url,
            "common_genres": output.shared_genres[:6],
            "common_artists": output.shared_artists[:6],
            "recommended_artists": output.recommended_artists[:6],
            "image_urls": image_urls,
            "tracks": tracks,
        }

    return render_template("results.html", match=session["result"])


# TODO Remove debug mode
if __name__ == "__main__":
    app.run(debug=True)
