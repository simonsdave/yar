"""This module is ..."""

import logging
import uuid

_logger = logging.getLogger("UTIL.%s" % __name__)


class APIKey(str):
    """This class generates a 32 character random string intend
    for use as an API key."""

    def __new__(cls, api_key):
        return str.__new__(cls, api_key)

    @classmethod
    def generate(cls):
        """Generate an api key. Returns an instance
        of ```APIKey```. There have been a few different
        implementations of this method. os.random() was used for
        a while but in the end the current implementation seemed
        to make the most sense because (i) nothing about the api
        key needs to be 'secure' (ii) wanted to be able
        to run a cluster of key services to api keys
        across multiple data centers so needed an approach which
        saw a very high probability that generated api keys
        where unique."""
        return cls(uuid.uuid4().hex)
