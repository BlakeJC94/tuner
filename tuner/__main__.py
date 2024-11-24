import logging

from tuner.core import tuner_match
from tuner.utils import display_match

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def main():
    """Main entrypoint for Tuner."""
    display_match(tuner_match())
    logging.info("Done!")
    return 0


if __name__ == "__main__":
    main()
