from _thread import *
 
import socket
import sys  

def serve_client(conn):
	welcome = "Fuck off!"
	conn.send(welcome.encode())
	while 1:
		pass

def main():
	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		print("Socket successfully created")
	except socket.error as err: 
		print ("socket creation failed with error %s" %(err)) 


	port = 20020

	s.bind(('', port))         
	print ("socket binded to %s" %(port)) 

	s.listen(5)

	while True:
		c,addr = s.accept()
		print("Connected with "+addr[0]+": "+str(addr[1]))
		start_new_thread(serve_client,(c,))

	s.close()

if __name__ == '__main__':
	main()