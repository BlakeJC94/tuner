import argparse
import logging

from tuner.core import tuner_match
from tuner.embeddings.compile import compile_embeddings
from tuner.utils import display_match

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

    display_match(tuner_match())
    logging.info("Done!")
    return 0


if __name__ == "__main__":
    main()
