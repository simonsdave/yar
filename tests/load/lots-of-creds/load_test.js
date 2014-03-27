{
	"language": "javascript",
	"views": {
		"random_set_of_creds": {
			"map": "function(doc) { if (doc.type.match(/^creds_v\\d+.\\d+/i)) var api_key = doc.basic.api_key; st = api_key.substr(api_key.length - 2, 2); x = parseInt(\"0x\" + st); key = Math.floor( (99.0 * x) / 255 ); emit(key, doc) }",
            "reduce": "_count"
		}
	}
}

