{
	"language": "javascript",
	"views": {
		"by_principal": {
			"map": "function(doc) { if (doc.type.match(/^creds_v\\d+.\\d+/i)) emit(doc.principal, doc) }"
		},
        "by_identifier": {
            "map": "function(doc) { if (doc.type.match(/^creds_v\\d+.\\d+/i)) { if (doc.basic) { emit(doc.basic.api_key, doc) } else { emit(doc.mac.mac_key_identifier, doc) } } }"
        }
	}
}
