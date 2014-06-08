{
	"language": "javascript",
	"views": {
        "by_identifier": {
            "map": "function(doc) { if (doc.type.match(/^creds_v\\d+.\\d+/i)) { if (doc.basic) { emit(doc.basic.api_key, doc) } else { emit(doc.mac.mac_key_identifier, doc) } } }"
        }
	}
}
