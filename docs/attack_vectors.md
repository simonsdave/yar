A variety of well known attack vectors exist for API management solutions.
Below is a list of these attack vectors and corresponding countermeasure(s).

### Reply Attacks
* [Wikipedia](http://en.wikipedia.org/wiki/Replay_attack)
* Countermeasure: Timestamp & Nonce

### Timing Attacks
* [Wikipedia](http://en.wikipedia.org/wiki/Timing_attack)
* [13 Aug '09 - A Lesson In Timing Attacks (or, Don’t use MessageDigest.isEquals)](http://codahale.com/a-lesson-in-timing-attacks/)
* Countermeasure: using [Keyczar's HmacKey.verify()](http://www.keyczar.org/pydocs/keyczar.keys.HmacKey-class.html#Verify)

### Resource Exhaustion (DoS & DDoS)
* [Wikipedia](http://en.wikipedia.org/wiki/Denial-of-service_attack)
* Countermeasure: ???

### :TODO: How to describe this?
* see [this](http://haacked.com/archive/2008/11/20/anatomy-of-a-subtle-json-vulnerability.aspx)
and think about the key server's responses
