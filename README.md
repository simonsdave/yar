API Management
==============

This repo is the result of Dave being convinced that it wouldn't be that
hard to write an API Management service. Conclusion? Well, this isn't complete
but it feels like this has gone a long way to demonstrating that a basic
service isn't massively hard to implement.

Prerequisites 
-------------
* code written and tested on Mac OS X 10.8.2 using
Python 2.7.2,
[nose 1.3.0](https://github.com/nose-devs/nose)
and [virtualenv 1.9.1](https://pypi.python.org/pypi/virtualenv)
* see [requirements.txt](https://github.com/simonsdave/apimgmt/blob/master/requirements.txt "requirements.txt") for the complete list of prerequisites

References
----------
* Authentication
 * [HTTP Authentication: MAC Access Authentication - note this is version 2 from 28 Nov '12](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02")
 * [OAuth 2.0](http://oauth.net/2/ "OAuth 2.0")
 * [macauthlib 0.5.0](https://github.com/mozilla-services/macauthlib) (pip install macauthlib)
* Tokenization
 * [JSONPath](http://goessner.net/articles/JsonPath/)
 * [Cybersource: Payment Tokenization - Using the Simple Order API](http://apps.cybersource.com/library/documentation/dev_guides/Payment_Tokenization/SO_API/Payment_Tokenization_SO_API.pdf)
* Technology
 * [couchdb-python](http://code.google.com/p/couchdb-python/)
 * [6 Feb '11: using Tornado as a proxy](https://groups.google.com/forum/?fromgroups=#!topic/python-tornado/TB_6oKBmdlA)
