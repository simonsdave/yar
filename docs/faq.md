### How can I generate a coverage report?
From yar's root directory run the following:
~~~~~
coverage erase
rm -rf ./coverage_report/
nosetests --with-coverage
coverage html
~~~~~
An HTML version of the coverage report can now be found in coverage_report/index.html

### Against which attack vectors does yar provide defenses?
See [Attack Vectors](Attack_Vectors.md).

### How are keys generated?
See [Key Generation](../yar/key_service#key-generation).

### What's an MAC?
See [this](http://en.wikipedia.org/wiki/Message_authentication_code).

### How is a MAC calculated?
yar implements the [OAuth 2.0 Message Authentication Code (MAC) Tokens](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02) specification.
This specification defines the details of how the MAC is calculated.
The only part not covered in the specification is how the extension (ext) is calculated.
The spec provides ext as a point of extensibility.
With yar, ext is a zero length byte array if a request has no body.
If the request does have a body the ext is the SHA1 of a byte array built by concatenating the request's content type with the request's body - to be clear it's a straight concatenation - there's no new newline between the content type and the request body

### What's a nonce?
See [this](http://en.wikipedia.org/wiki/Cryptographic_nonce).

### How do I generate a nonce?
When generating a nonce it's important that:

1. the nonce is long enough - an 8-byte nonce should be long enough
1. the nonce is sufficiently random - on UNIX like systems 
use [/dev/urandom](http://en.wikipedia.org/wiki//dev/random) as a source for the nonce

It's worth taking a look at the openssl command line tool because the tool can easily cover off both the length and sufficiently random requirements. Sample command:
~~~~~
openssl rand -hex 8
~~~~~

### How do I calculate a MAC in X where X = your favorite programming language?
This question surfaces because yar:
* is written in Python
* implements the [OAuth 2.0 Message Authentication Code (MAC) Tokens](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02) specification
* uses [Keyczar](http://www.keyczar.org/) to generate keys, generate MACs and compare MACs

For an answer by example, take a look @ [yarcurl](../bin/yarcurl)
which is a [Bash](http://en.wikipedia.org/wiki/Bash_%28Unix_shell%29) script 
and if MAC computation can be done in [Bash](http://en.wikipedia.org/wiki/Bash_%28Unix_shell%29)
shouldn't it be possible to compute an MAC in pretty much any language:-)

Here's a quick summary of the steps for generating a MAC:
* build a normalized request string as defined by the
[OAuth 2.0 Message Authentication Code (MAC) Tokens](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02) spec - see above comment on how yar calculates/uses the spec's extension (ext) and how to "correctly" generate a nonce
* armed with the normalized request string the next step is to use your favorite language's HMAC function to compute the MAC using the MAC Key and the normalized request string
* when computing the MAC care needs to be taken because of the way [Keyczar](http://www.keyczar.org/) base64 encodes keys - yar asks [Keyczar](http://www.keyczar.org/) to generate a 256-bit (32-byte) key which is then base64 encoded:
  * the base64 encoding is "URL safe" which means using an using an alphabet with - replacing + and _ replacing /
  * the base64 encoding also removes any equal sign (=) padding from the end of the byte array
* the result of using the above base64 encoding schema against a 256-bit key is that [Keyczar](http://www.keyczar.org/) always provides yar with a 43 byte key (yar calls this the MAC Key)
* the above is important because unless [Keyczar](http://www.keyczar.org/) is available for your
favorite language you'll have to reverse the above encoding scheme for the MAC Key before passing
the key to the HMAC function - this isn't hard as long as you know the right steps - here's
how it's done in a bash script (see [yarcurl](../bin/yarcurl) for the complete story):

~~~~~
MAC_KEY=$(echo -n $MAC_KEY | sed -e "s/\-/\+/g" | sed -e "s/\_/\//g")=
MAC_KEY=$(echo -n $MAC_KEY | base64 --decode)
~~~~~

* so the steps to prepare the key are:
  1. replace all -s with +s
  1. replace all _s with /s
  1. add an = to the end
  1. base64 decode the key

### How do I debug authentication failures?
This is hard. It's the one knock against using MACs.
First step would be to restart the [Auth Service](../yar/auth_service) using debug level logging.
This will generate additional logging output but more importantly it will generate
lots of additional HTTP X-Yar-Auth- headers that provide detailed insight into how
the [Auth Service](../yar/auth_service) is computing the MAC.
99% of the time reviewing this output will help you track down the problem.

### What's up with the name "yar"?
Was looking for a short name that came from a
character in a "good" movie or TV show that related in some way to security.
Top three choices where
[Yar](http://en.wikipedia.org/wiki/Tasha_Yar),
[Worf](http://en.wikipedia.org/wiki/Worf)
and
[Seraph](http://en.wikipedia.org/wiki/Seraph_%28The_Matrix%29).
Yar won because it was the shortest,
sounded like a roar
and my kids could not pronounce Seraph.

### What other API Management solutions exist?
* [API Umbrella](https://github.com/NREL/api-umbrella/)
* [19 Oct '11 - ProgrammableWeb - 11 API Management Services](http://blog.programmableweb.com/2011/10/19/api-service-provider-roundup/)
* [5 Oct '14 - API Evangelist - Taking A Fresh Look At What Open Source API Management Architecture Is Available](http://apievangelist.com/2014/10/05/taking-a-fresh-look-at-what-open-source-api-management-architecture-is-available)

### How do I add a new authentication scheme to yar?
Short answer is "add/change a bunch of code to a few different spots"
with those spots being (assume new authentication scheme is called new_auth):
* add new_auth.py to [yar/yar/util](../yar/util)
just like [basic.py](../yar/util/basic.py)
and [mac.py](../yar/util/mac.py)
* update [yar/tests/tests-load/locustfile.py](../tests/tests-load/locustfile.py)
