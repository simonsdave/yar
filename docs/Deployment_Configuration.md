* Internet into a switch with [port mirroring](http://en.wikipedia.org/wiki/Port_mirroring) capability
* mirrored port on switch sends traffic to [Snort](http://www.snort.org/) acting as phase 1 [IDS](http://en.wikipedia.org/wiki/Intrusion_detection_system) - note, this style of Snort deployment is well suited to IDS - if we wanted [IPS](http://en.wikipedia.org/wiki/Intrusion_prevention_system) we'd deploy Snort as a proxy between Internet and Firewall (see below)
* Firewall - probably Cisco but if not next most popular choice would be
Linux and [IP Tables](http://en.wikipedia.org/wiki/Iptables) with some kind
of simplifying layers on top of IP tables to make it easier to manage - probably
would want to base the firewall on a [firewall centric Linux distro](http://en.wikipedia.org/wiki/List_of_router_and_firewall_distributions)
* maybe load balancer (possibly haproxy) across SSL termination tier (see note below)
* SSL Termination - nginx or Apache (using mod_security) - 2 nodes for high availability - active/passive configuration - single IP presented to Firewall - [Virtual Router Redundancy Protocol (VRRP)](http://en.wikipedia.org/wiki/Virtual_Router_Redundancy_Protocol) to automagically manage assignment of the IP to the correct/available node - could run a cluster of SSL term active/passive pairs so the SSL term tier can be scaled horizontally - in this case the firewall or something like haproxy would have to load balance across the SSL term tier
* IDS Phase 2 - [Snort](http://www.snort.org/) again as above deployed on mirror port of a switch
* load balancer to distribute traffic across auth servers - node(s) used for SSL Termination could do this except we have snort in there or could use haproxy, nginx or Apache
* auth servers make requests to key servers using "client side haproxy pattern" & key servers likewise do the same to couchdb instances
* after authentication, authorization & accounting (done in auth server) traffic needs to be routed to app server or key server (yes requests to the key server should go thru the auth server too!)

