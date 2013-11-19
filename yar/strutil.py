"""This module contains a series of utilities for manipulating valueings."""


def make_http_header_value_friendly(value):
    """The caller wants to return ```value``` in an HTTP response
    where ```value``` is the value for an HTTP header. This won't work
    so well if ```value``` contains things like tabs and newlines.
    This function creates a version of ```value``` that can safely
    be used as the value for an HTTP header."""
    if value is None:
        return "<None>"
    value = str(value)
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    value = value.replace("\t", "\\t")
    return value
