### Key Concepts
* a **policy** is a (written) statement of intent
* a policy are implemented by a **procedure**
* (application) **controls** ensure procedures are executed
as per the related policy
* **authentication** verifies **identity**
* **access control** refers to the control of access to resources
* an **access control model** describes the operations
a principal can perform on an object
* there are different types of access control models:
  * [discretionary access control (DAC)](http://en.wikipedia.org/wiki/Discretionary_access_control)
  * [mandatory access control (MAC)](http://en.wikipedia.org/wiki/Mandatory_access_control)
  * [role based access control (RBAC)](http://en.wikipedia.org/wiki/Role_based_access_control)
* it should be possible to explicitly revoke access to a resource
* **authorization** updates an access control model
* **access approval** uses the access control model to determine
if a principal is permitted to access a resource
* **[separation of duties (SoD) ](http://en.wikipedia.org/wiki/Separation_of_duties)**
describes the concept of multiple individuals being required to complete a single task
* separation of duties is aka segregation of duties
* **accounting** records all authentication, authorization
and access approval activity
* **tokenization** substitutes sensitive data in a request with non-sensitive token
* tokens and their corresponding sensitive data are stored
in a (highly) secure **token vault**
* the purpose of tokenization is to minimize the number
of systems/services that touch sensitive data
ie tokenization reduces scope

### Patterns yar Enables
* something about, someone configures it, someone approves it and someone
else launches it - how does yar? SoD
* policy = 
* procedure =
~~~~~
/
~~~~~

### Open Questions
* does yar support the notion of resource ownership? can't use DAC
if there's no concept of resource ownership.

### References
* [What is the meaning of Subject vs. User vs. Principal in a Security Context?](http://stackoverflow.com/questions/4989063/what-is-the-meaning-of-subject-vs-user-vs-principal-in-a-security-context)
* [Def'n - Wikipedia: authentication, authorization, accounting (AAA)](http://en.wikipedia.org/wiki/AAA_protocol)
* [CompTIA Security+ TechNotes - Access Control](http://www.techexams.net/technotes/securityplus/mac_dac_rbac.shtml)
* [Def'n - Wikipedia: Tokenization (data security)](http://en.wikipedia.org/wiki/Tokenization_(data_security))
* [Video: "60 Seconds Smarter on Tokenization" from Intel](https://www.youtube.com/watch?feature=player_embedded&v=-DqCtdc30LY)
* [Def'n - http://searchsecurity.techtarget.com/: tokenization](http://searchsecurity.techtarget.com/definition/tokenization)

### Possible Related References
* [Cloud Security Alliance (CSA) Software Defined Perimeter (SDP)](https://cloudsecurityalliance.org/research/sdp/)
* [Security Operations: Moving to a Narrative-Driven Model](http://www.securityweek.com/security-operations-moving-narrative-driven-model)
