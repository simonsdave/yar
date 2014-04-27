{
	"language": "javascript",
	"views": {
		"by_principal": {
			"map": "function(doc) { if (doc.type.match(/^creds_v\\d+.\\d+/i)) emit(doc.principal, doc) }"
		}
	}
}
