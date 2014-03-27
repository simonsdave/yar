{
	"language": "javascript",
	"views": {
		"random_set_of_creds": {
			"map": "function(doc) { if (doc.type.match(/^creds_v\\d+.\\d+/i)) var api_key = doc.basic.api_key; var num_digits = 4; var digits = \"0x\" + api_key.substr(api_key.length - num_digits, num_digits); var div = Math.pow(2.0, num_digits * 8) - 1; var key = Math.floor((99.0 * parseInt(digits)) / 0xffff); emit(key, doc) }",
            "reduce": "_count"
		}
	}
}

