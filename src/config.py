import socket

HOSTNAME_MAX_LEN = 249
CONTENT_ID_MAX_LEN = 256
LOCATION_ID_MAX_LEN = 256


DNS_IP = socket.gethostname()
DNS_PORT = 1234
DNS_MAX_LISTEN = 100

LB_CLIENT_MAX_LISTEN = 10
LB_CLIENT_LISTEN_PORT = 10000
LB_HEARTBEAT_PORT = 10002
LB_HEARTBEAT_TIME = 1	# seconds
MAX_CLIENT_REQUESTS = 10
CLIENT_REQUEST_PORT = 10003

EDGE_HEARTBEAT_LISTENER_PORT = 20000
EDGE_HEARTBEAT_TIME = 1
MAX_EDGE_SERVERS = 5

MSG_DELAY = 5

ORIGIN_SERVER_PORT = 40000
ORIGIN_HEARTBEAT_TIME = 1
ORIGIN_HEARTBEAT_PORT = 40001
ORIGIN_CONTENT_PROVIDER_PORT = 40002