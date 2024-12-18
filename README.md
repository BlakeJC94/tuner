# [tuner](https://tunerapp.xyz/)
An application to find other Spotify users with similar music tastes

## Usage
Create a `.env` file with the following values
```
SPOTIPY_CLIENT_ID="..."
SPOTIPY_CLIENT_SECRET="..."
SPOTIPY_REDIRECT_URI="..."
PINECONE_API_KEY="..."
LASTFM_API_KEY="..."
LASTFM_API_SECRET="..."
```

Install the app with `uv sync` and start a local web server with `uv run python app.py`

The CLI proof of concept can be run with `uv run tuner`


## References
* [Spotify genre list from andytlr](https://gist.github.com/andytlr/4104c667a62d8145aa3a)

## Development

This requires Python >= 3.11, and dependencies are managed by UV `0.5.1`

Adding dependencies:
```
uv add [--dev] <package-name>
```

Compile requirement.txt for deployment
```
uv export --no-hashes --no-dev > requirements.txt
```
