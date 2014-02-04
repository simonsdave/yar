"""This module contains JSON schemas which can be used to validate
JSON bodies of request to and responses from the key server."""


"""```create_creds_request``` is a JSON schema used to validate
create credentials requests to the key server."""
create_creds_request = {
    "type": "object",
    "properties": {
        "principal": {
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
        "principal",
    ],
    "additionalProperties": False,
}


"""```get_creds_response``` is a JSON schema used to validate
the key server's response to get creds request."""
get_creds_response = {
    "$schema": "http://json-schema.org/draft-04/schema#",
#    "id": "http://api.cloudfeaster.com/v1.00/spider_metadata",
    "title": "Get Creds Response",
    "description": "Get Creds Response",
    "type": "object",
    "oneOf": [
        {
            "type": "object",
            "properties": {
                "basic": {
                    "type": "object",
                    "properties": {
                        "api_key": {
                            "type": "string",
                            "minLength": 1,
                        },
                    },
                    "required": [
                        "api_key",
                    ],
                    "additionalProperties": False,
                },
                "is_deleted": {
                    "type": "boolean",
                },
                "principal": {
                    "type": "string",
                    "minLength": 1,
                },
                "links": {
                    "type": "object",
                    "properties": {
                        "self": {
                            "type": "object",
                            "properties": {
                                "href": {
                                    "type": "string",
                                    "minLength": 1,
                                },
                            },
                        },
                    },
                },
            },
            "required": [
                "basic",
                "is_deleted",
                "principal",
                "links",
            ],
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {
                "hmac": {
                    "type": "object",
                    "properties": {
                        "mac_algorithm": {
                            "type": "string",
                            "enum": [
                                "hmac-sha-1",
                                "hmac-sha-256",
                            ],
                        },
                        "mac_key": {
                            "type": "string",
                            "minLength": 1,
                        },
                        "mac_key_identifier": {
                            "type": "string",
                            "minLength": 1,
                        },
                    },
                    "required": [
                        "mac_algorithm",
                        "mac_key",
                        "mac_key_identifier",
                    ],
                    "additionalProperties": False,
                },
                "is_deleted": {
                    "type": "boolean",
                },
                "principal": {
                    "type": "string",
                    "minLength": 1,
                },
                "links": {
                    "type": "object",
                    "properties": {
                        "self": {
                            "type": "object",
                            "properties": {
                                "href": {
                                    "type": "string",
                                    "minLength": 1,
                                },
                            },
                        },
                    },
                },
            },
            "required": [
                "hmac",
                "is_deleted",
                "principal",
                "links",
            ],
            "additionalProperties": False,
        },
    ],
}


"""```create_creds_response``` is a JSON schema used to validate
the key server's response to create creds request."""
create_creds_response = get_creds_response
