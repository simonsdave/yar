{
	"language": "javascript",
	"views": {
		"all": {
			"map": "function(doc) { if (doc.type.match(/^creds_v\\d+.\\d+/i)) var api_key = doc.basic.api_key; var num_digits = 4; var digits = \"0x\" + api_key.substr(0, num_digits); var div = Math.pow(2.0, num_digits * 8) - 1; var key = 1 + Math.floor((1000.0 * parseInt(digits)) / (1.0 + 0xffff)); emit(key) }"
		}
	}
}

