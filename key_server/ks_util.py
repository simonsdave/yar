"""This module contains a collection of key server specific utilities."""

def _filter_out_non_model_creds_properties(creds):
    """When a dictionary representing a set of credentials
    is created, the dictionary may contain entries that are
    no part of the externally exposed model. This function
    takes a dictionary (```dict```), selects only the
    model properties in ```dict``` and returns a new
    dictionary containing only the model properties."""
    rv = {}
    keys = [
        "is_deleted",
        "mac_algorithm",
        "mac_key",
        "mac_key_identifier",
        "owner"
    ]
    for key in keys:
        if key in creds:
            rv[key] = creds[key]
    return rv
