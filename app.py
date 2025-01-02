import asyncio
import logging
import random
from dataclasses import asdict

import spotipy
from dotenv import load_dotenv
from flask import Flask, render_template, session, request, redirect, jsonify
from flask_session import Session

from tuner.core import tuner_match, tuner_delete
from tuner.db import Artist
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


@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/delete')
def delete():
    session['delete'] = True

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope=SCOPE,
        cache_handler=cache_handler,
        show_dialog=True,
    )

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    try:
        tuner_delete(spotipy.Spotify(auth_manager=auth_manager))
        message = 'Your data has been deleted successfully.'
    except Exception as err:
        message = f"Error deleting your data, please try again. ({err})"

    session['delete'] = False
    return render_template("deleted.html",message=message)


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

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    # Signed in, display data
    return redirect("/delete") if session.get('delete', None) else redirect("/results")


@app.route("/results", methods=["GET", "POST"])
def results():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect("/")

    sp = spotipy.Spotify(auth_manager=auth_manager)

    try:
        output = tuner_match(sp)
    except Exception:
        return render_template("in-progress.html")

    dim = 160
    image_urls = []
    for a in sp.artists(output.artist_ids)["artists"]:
        foo = [i["url"] for i in a["images"] if i["width"] == dim]
        if not foo:
            continue
        image_urls.append((foo[0], a["name"]))
    image_urls = random.sample(image_urls, min(10, len(image_urls)))

    session["result"] = {
        "user_id": output.user_md.id,
        "name": output.match_md.display_name,
        "score": f"{100 * output.score:.2f}",
        "profile_link": output.match_md.url,
        "common_genres": output.shared_genres[:6],
        "common_artists": output.shared_artists[:6],
        "recommended_artists": output.recommended_artists[:6],
        "image_urls": image_urls,
        "artists": [asdict(a) for a in output.sp_artists],
        "playlist_data": None,
    }

    return render_template("results.html", match=session["result"])


@app.route("/playlist", methods=["POST"])
def playlist():
    tracks = session.get("tracks", None)
    if tracks is None:
        cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        access_token = auth_manager.get_cached_token()["access_token"]
        artists = [Artist(**a) for a in session["result"]["artists"]]
        tracks = asyncio.run(get_playlist(access_token, artists))
        tracks = random.sample(tracks, min(16, len(tracks)))
        tracks = [asdict(t) for t in tracks]
        session["tracks"] = tracks
    return jsonify(tracks)


@app.route("/save", methods=["POST"])
def save():
    if session["result"]["playlist_data"]:
        return jsonify()

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return jsonify()

    sp = spotipy.Spotify(auth_manager=auth_manager)

    user = session["result"]["user_id"].split(":")[-1]
    name = f"Tuner - {session['result']['name']}"
    if "test" in name:
        return jsonify()
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
        [t["uri"] for t in session["tracks"]],
    )
    playlist_data = {
        "name": name,
        "external_url": playlist["external_urls"]["spotify"],
    }
    session["result"]["playlist_data"] = playlist_data
    return jsonify()


if __name__ == "__main__":
    app.run(debug=False, port=5000)
