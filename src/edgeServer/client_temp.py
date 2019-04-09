import socket                   # Import socket module
import sys  
sys.path.insert(0, "../")
from messages.content_related_messages import *

s = socket.socket()             # Create a socket object
host = "127.0.0.1"  #Ip address that the TCPServer  is there
port = 30001                    # Reserve a port for your service every new transfer wants a new port or you must wait.

s.connect((host, port))
message = ContentRequestMessage(1, 0)
message.send(s)

with open('as.png', 'wb') as f:
    print('file opened')
    while True:
        mes = ContentMessage(0, 0)
        print('receiving data...')
        mes.receive(s)
        print(mes.content_id)
        print(mes.seq_no)
        data = mes.data
        if not data:
            break
        # write data to a file
        f.write(data)

f.close()
print('Successfully get the file')
s.close()
print('connection closed')
