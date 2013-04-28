"""This module contains JSON schemas that can be used to validate
JSON request and response bodies between the various services in
the API management solution."""

#-------------------------------------------------------------------------------
"""```key_server_requent``` is a JSON schema used to validate
create credentials requests to the key server."""

key_server_create_creds_request = {
	"type" : "object",
	"properties" : {
		"owner": {
			"type": "string",
			"minLength": 1
		},
	},
	"required": [
		"owner",
	],
	"additionalProperties": False,
}

#-------------------------------------------------------------------------------
"""```key_server_response``` is a JSON schema used to validate
responses from the key server."""

key_server_response = {
	"type" : "object",
	"properties" : {
		"is_deleted": {
			"type": "boolean"
		},
		"mac_algorithm": {
			"type": "string",
			"anyOf": [
				{"required":["hmac-sha-1"]},
				{"required":["hmac-sha-256"]},
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
	},
	"required": [
		"is_deleted",
		"mac_algorithm",
		"mac_key",
		"mac_key_identifier",
		"owner",
	],
	"additionalProperties": False,
}

#------------------------------------------------------------------- End-of-File
