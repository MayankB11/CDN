Animesh
10.146.216.240
Origin server 1
Edge server 30005 0
Client 1

Bhushan
10.145.245.246
Load balancer backup
Origin 2
Edge server 30005 1

Nisarg
10.146.197.110
Load 1
Content provider
Client 2

Prathamesh
10.146.137.166
DNS
Edge server 30005 2
Client 0



Order of - running code
DNS - PC
LB1 - Nisarg
LB2 - Bhushan
O1 - Animesh
O2 - Bhushan
CP - Nisarg
E1 - PC
E2 - Animesh
E3 - Bhushan
Client - Nisarg, Animesh, PC


Test cases.
Load balancer IPs stored in DNS. 
Content provider sends data to origin, replicated. 
edge server sends heartbeats.
1. Client requests file. Fetch from origin. Give to client. 
2. Client requests file. Give to client. 
3. Fault tolerance
	a. Edge server fails while transfer is going on. 
	b. Edge server fails while transfer going on between origin and edge
	c. Origin fails when transfer between content provider and origin taking place.
	d. Origin fails when transfer between edge and origin
	e. Origin fails when transfer between origins. Comes up. 
	f. Load balancer primary fails
	g. Comes up.