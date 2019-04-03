'''
Code for dummy DNS. It provides two services:
1) add_entry(hostname, ip, host)
2) get_ip(hostname)

services can be accessed using messages having the folowing structure (256 bytes):
 ------------------------------------------------------------------------------
| SERVICE_ID (1 byte) | Hostname (249 bytes) | IPv4 (4 bytes) | Port (2 bytes) |
 ------------------------------------------------------------------------------

SERVICE_ID : 1 - add_entry
			 2 - get_ip

Reply for get_ip is of the form (24 bytes):
 -----------------------------------------------
| IP block1 | IP block2 | IP block3 | IP block4 |
 -----------------------------------------------

IP block (6 bytes):
 ---------------------------------
| IPv4 (4 bytes) | Port (2 bytes) |
 ---------------------------------

'''

