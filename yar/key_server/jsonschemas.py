"""This module contains JSON schemas which can be used to validate
JSON bodies of request to and responses from the key server."""


"""```create_creds_request``` is a JSON schema used to validate
create credentials requests to the key server."""
create_creds_request = {
    "type": "object",
    "properties": {
        "owner": {
            "type": "string",
            "minLength": 1
        },
        "auth_scheme": {
            "type": "string",
            "enum": [
                "hmac",
                "basic",
            ],
        },
    },
    "required": [
        "owner",
    ],
    "additionalProperties": False,
}


"""```get_creds_response``` is a JSON schema used to validate
the key server's response to get creds request."""
get_creds_response = {
    "type": "object",
    "properties": {
        "is_deleted": {
            "type": "boolean"
        },
        "mac_algorithm": {
            "type": "string",
            "enum": [
                "hmac-sha-1",
                "hmac-sha-256",
            ],
        },
        "mac_key": {
            "type": "string",
            "minLength": 1
        },
        "mac_key_identifier": {
            "type": "string",
            "minLength": 1
        },
        "owner": {
            "type": "string",
            "minLength": 1
        },
        "links": {
            "type": "object",
            "properties": {
                "self": {
                    "type": "object",
                    "properties": {
                        "href": {
                            "type": "string",
                            "minLength": 1
                        }
                    }
                }
            }
        },
    },
    "required": [
        "is_deleted",
        "mac_algorithm",
        "mac_key",
        "mac_key_identifier",
        "owner",
        "links",
    ],
    "additionalProperties": False,
}


"""```create_creds_response``` is a JSON schema used to validate
the key server's response to create creds request."""
create_creds_response = get_creds_response
