# Components
# Get heartbeat
# Serve as primary when needed - functionalities - 
	# 1. Change state
	# 2. Serve edge servers
	# 3. Serve content providers
# Back up data received from primary

class State(Enum):
	PRIMARY = 1
	SECONDARY = 2
def backup_data():
	pass
def serve_edge_server():
	pass
def serve_content_provider():
	pass
def main():
	# Receive heartbeat and change state accordingly
	pass
if __name__ == '__main__':
	main()