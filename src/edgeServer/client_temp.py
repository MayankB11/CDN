import socket                   # Import socket module
import sys  
sys.path.insert(0, "../")
from messages.content_related_messages import *
import hashlib
import os

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.digest()

s = socket.socket()             # Create a socket object
host = "127.0.0.1"  #Ip address that the TCPServer  is there
port = 30001                    # Reserve a port for your service every new transfer wants a new port or you must wait.

s.connect((host, port))
message = ContentRequestMessage(1, 0)
message.send(s)

file_des = FileDescriptionMessage(0, 0, '', 0)
file_des.receive(s)
print(file_des.file_name)
print(file_des.content_id)
print(file_des.file_size)
with open('rec_' + file_des.file_name, 'wb') as f:
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
print('Successfully got the file')
new_filename = 'rec_' + file_des.file_name
# check md5
if md5('rec_' + file_des.file_name) == file_des.md5_val:
    print("MD5 Matched!")
else:
    print("MD5 didn't match")
s.close()
print('connection closed')
