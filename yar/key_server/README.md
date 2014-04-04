To start the Key Server:
~~~~~
key_server
~~~~~
By default the Key Server will attempt to listen on 127.0.0.1:8070 and connect to
a [Key Store](https://github.com/simonsdave/yar/wiki/Key-Store)
at localhost:5984/creds.
For a complete list of the Key Server's command line options try:
~~~~~
key_server --help
~~~~~
The Key Server is configured using command line options.
No configuration file is used.

All credentials are "owned" by someone.
An owner's identity is represented below as an opaque string at least one character long.
To create a set of credentials:
~~~~~~
curl \
  -v \
  -X POST \
  -H "Content-Type: application/json; charset=utf8" \
  -d "{\"owner\":\"simonsdave@gmail.com\"}" \
  http://localhost:8070/v1.0/creds
~~~~~~
To get an existing set of credentials:
~~~~~
curl \
  -v \
  -X GET \
  http://localhost:6969/v1.0/creds/<MAC key identifier>
~~~~~
To get all credentials currently saved in the
[Key Store](https://github.com/simonsdave/yar/wiki/Key-Store):
~~~~~~
curl \
  -s \
  -X GET \
  http://localhost:8070/v1.0/creds
~~~~~~
To get all credentials with a specific owner:
~~~~~
curl -X GET http://localhost:8070/v1.0/creds?owner=<owner>
~~~~~
To get all credentials including those that have been deleted:
~~~~~
curl -X GET http://localhost:8070/v1.0/creds?deleted=true
~~~~~
To delete a set of existing credentials:
~~~~~
curl \
  -v \
  -X DELETE \
  http://localhost:6969/v1.0/creds/<MAC key identifier>
~~~~~

### Key Generation

[Keyczar](http://www.keyczar.org/) is used to generate MAC keys.
Specifically, *keyczar.keys.HmacKey.Generate()* is used to generate
a 256 bit key.
See [mac.MACKey.generate()](../util/mac.py#L159)
for all the details.

MAC key identifiers are generated using Python's
[uuid.uuid4()](http://docs.python.org/2/library/uuid.html).
See [mac.MACKeyIdentifier.generate()](../util/mac.py#L137)
for all the details.

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
