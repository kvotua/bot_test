import socket
import os

HOST = socket.gethostname()
os.environ['HOST_TRUE'] = HOST