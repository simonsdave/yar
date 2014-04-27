To start the Key Server:

~~~~~
key_server
~~~~~

By default the Key Server will attempt to listen on 127.0.0.1:8070 and connect to
a [Key Store](../key_store) at 127.0.0.1:5984/creds.
For a complete list of the Key Server's command line options try:

~~~~~
key_server --help
~~~~~

The Key Server is configured using command line options.
No configuration file is used for configuration.

All credentials are associated with a principal.
Principals are represented below as an opaque string at least one character long.
To create a set of credentials for the principal dave@example.com
and for use with
[MAC](http://en.wikipedia.org/wiki/Message_authentication_code):
Autentication:

~~~~~~
curl \
  -s \
  -X POST \
  -H "Content-Type: application/json; charset=utf8" \
  -d "{\"principal\":\"dave@example.com\", \"auth_scheme\":\"mac\"}" \
  http://127.0.0.1:8070/v1.0/creds
~~~~~~

To get an existing set of credentials:

~~~~~
curl -s http://127.0.0.1:8070/v1.0/creds/<MAC key identifier>
~~~~~

To get all credentials associated with a principal:

~~~~~
curl http://127.0.0.1:8070/v1.0/creds/?principal=dave@example.com
~~~~~

To delete a set of existing credentials:

~~~~~
curl -X DELETE http://127.0.0.1:8070/v1.0/creds/<MAC key identifier>
~~~~~

To get all credentials including those that have been deleted:

~~~~~
curl http://127.0.0.1:8070/v1.0/creds/?deleted=true
~~~~~

### Key Generation

[Keyczar](http://www.keyczar.org/) is used to generate MAC Keys.
Specifically, *keyczar.keys.HmacKey.Generate()* is used to generate
a 256 bit key.
See [mac.MACKey.generate()](../util/mac.py#L159)
for all the details.

MAC Key Identifiers are generated using Python's
[uuid.uuid4()](http://docs.python.org/2/library/uuid.html).
See [mac.MACKeyIdentifier.generate()](../util/mac.py#L137)
for all the details.
A question that's sometimes asked is "are UUID4 (globally) unique and/or secure".
Short answer is "yes". Rather than providing the long answer here, we'll reference
key materials to help you get to the same "yes" short answer that yar designers
arrived at:
* [this](http://stackoverflow.com/questions/703035/when-are-you-truly-forced-to-use-uuid-as-part-of-the-design/786541#786541) answer should convince the reader of the "yes" short answer but in case not continue on reading the 
articles referenced below
* [Python's UUID objects according to RFC 4122](https://docs.python.org/2.7/library/uuid.html)
* [RFC 4122](http://tools.ietf.org/html/rfc4122.html)

Nonces are generated using Python's
[os.urandom()](http://docs.python.org/2/library/os.html#os-miscfunc).
See [mac.Nonce.generate()](../util/mac.py#L42)
for all the details.

### Key Generation References
Above described how keys are generated.
The references below outline the logic to arrive at this implementation.

* [OAuth 2.0 Message Authentication Code, Section 6.5 = Entropy of MAC Keys](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-6.5) - key points:

> It is equally important that the [pseudo-random number generator (PRNG)](http://en.wikipedia.org/wiki/Pseudorandom_number_generator) used to generate these MAC keys be of sufficiently high quality. Many PRNG implementations generate number sequences that may appear to be random, but which nevertheless exhibit patterns or other weaknesses which make cryptanalysis or brute force attacks easier. Implementers should be careful to use cryptographically secure PRNGs to avoid these problems.

* [Python: Random is barely random at all?](http://stackoverflow.com/questions/2145510/python-random-is-barely-random-at-all) is an excellent article on PRNGs in general and some Python specifics too - well
worth the time to read and digest this article.

* [Cryptographically secure pseudorandom number generator (CSPRNG)](http://en.wikipedia.org/wiki/Cryptographically_secure_pseudorandom_number_generator)

* [Python's os.urandom() function](http://docs.python.org/2/library/os.html#os-miscfunc) - key points:

> This function returns random bytes from an OS-specific randomness source. The returned data should be unpredictable enough for cryptographic applications, though its exact quality depends on the OS implementation. On a UNIX-like system this will query /dev/urandom ...

* [/dev/random & /dev/urandom](http://en.wikipedia.org/wiki//dev/random)
