import argparse
import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
from dotenv import load_dotenv

from tuner.core import tuner_match
from tuner.embeddings.compile import compile_embeddings
from tuner.utils import display_match
from tuner.globals import SCOPE

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def main():
    """Main entrypoint for Tuner."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--compile", action="store_true")
    args = parser.parse_args()

    if args.compile:
        compile_embeddings()
        return 0

    logger.info("Logging into Spotify")
    load_dotenv()
    cache_handler = MemoryCacheHandler()
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=SCOPE,
            show_dialog=True,
            cache_handler=cache_handler,
        ),
    )

    display_match(tuner_match(sp))
    logging.info("Done!")
    return 0


if __name__ == "__main__":
    main()
