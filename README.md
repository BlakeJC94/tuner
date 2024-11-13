# tuner
An application to find other Spotify users with similar music tastes

## Usage
Create a `.env` file with the following values
```
SPOTIPY_CLIENT_ID="..."
SPOTIPY_CLIENT_SECRET="..."
SPOTIPY_REDIRECT_URI="..."
```


## References
* [Spotify genre list from andytlr](https://gist.github.com/andytlr/4104c667a62d8145aa3a)

## Development

This requires Python >= 3.11, and dependencies are managed by UV `0.5.1`

To add dependencies, use `uv add [--dev] <package-name>`, and update the requirements
files using `uv export [--dev] > requirements[-dev].txt`.
