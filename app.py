import asyncio
import logging
import random
from dataclasses import asdict

import spotipy
from dotenv import load_dotenv
from flask import Flask, render_template, session, request, redirect
from flask_session import Session

from tuner.core import tuner_match
from tuner.playlist import get_playlist
from tuner.globals import SCOPE

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = "foobar"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = ".flask_session/"
Session(app)

app.logger.setLevel(logging.INFO)


# Define pages
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope=SCOPE,
        cache_handler=cache_handler,
        show_dialog=True,
    )

    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"), as_dict=False)
        return redirect("/results")

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    # Step 3. Signed in, display data
    return redirect("/results")


@app.route("/results", methods=["GET", "POST"])
def results():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect("/")

    sp = spotipy.Spotify(auth_manager=auth_manager)

    if "result" not in session:
        output = tuner_match(sp)

        dim = 160
        image_urls = []
        for a in sp.artists(output.artist_ids)["artists"]:
            foo = [i["url"] for i in a["images"] if i["width"] == dim]
            if not foo:
                continue
            image_urls.append(foo[0])
        image_urls = random.sample(image_urls, min(6, len(image_urls)))

        access_token = auth_manager.get_cached_token()["access_token"]
        artists = output.sp_artists
        tracks = asyncio.run(get_playlist(access_token, artists))
        tracks = [asdict(t) for t in tracks]

        session["result"] = {
            "user_id": output.user_md.id,
            "name": output.match_md.display_name,
            "score": f"{100 * output.score:.2f}",
            "profile_link": output.match_md.url,
            "common_genres": output.shared_genres[:6],
            "common_artists": output.shared_artists[:6],
            "recommended_artists": output.recommended_artists[:6],
            "image_urls": image_urls,
            "tracks": tracks,
            "playlist_data": None,
        }

    if request.method == "POST" and not session["result"]["playlist_data"]:
        user = session["result"]["user_id"].split(":")[-1]
        name = f"Tuner - {session['result']['name']}"
        if "test" not in name:
            matching_playlists = []
            playlists = sp.user_playlists(user)
            while playlists:
                for i, playlist in enumerate(playlists["items"]):
                    if playlist["name"].startswith(name):
                        matching_playlists.append(playlist["name"])
                if playlists["next"]:
                    playlists = sp.next(playlists)
                else:
                    playlists = None

            n_matching = len(matching_playlists)
            if n_matching > 0:
                name = f"{name} ({n_matching+1})"

            playlist = sp.user_playlist_create(
                user,
                name,
                public=True,
                collaborative=False,
                description="Suggested playlist from Tuner",
            )
            sp.user_playlist_add_tracks(
                user,
                playlist["id"],
                [t["uri"] for t in session["result"]["tracks"]],
            )
            playlist_data = {
                "name": name,
                "external_url": playlist["external_urls"]["spotify"],
            }
            session["result"]["playlist_data"] = playlist_data

    return render_template("results.html", match=session["result"])


# TODO Remove debug mode
if __name__ == "__main__":
    app.run(debug=False, port=5000)
