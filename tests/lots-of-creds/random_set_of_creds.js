{
	"language": "javascript",
	"views": {
		"all": {
			"map": "function(doc) { if (doc.type.match(/^creds_v\\d+.\\d+/i)) { var identifier = \"\"; value = \"\"; if (doc.basic) { identifier = doc.basic.api_key; value = doc.basic } else { identifier = doc.mac.mac_key_identifier; value = doc.mac }; var num_digits = 4; var digits = \"0x\" + identifier.substr(0, num_digits); var div = Math.pow(2.0, num_digits * 8) - 1; var key = 1 + Math.floor((100.0 * parseInt(digits)) / (1.0 + 0xffff)); emit(key, value) } }"
		}
	}
}

