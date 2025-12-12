import socket
print(socket.gethostbyname('a9fea9fe'))      # "169.254.169.254" ✓
print(socket.gethostbyname('2130706433'))      # "127.0.0.1" ✓
print(socket.gethostbyname('0251.0376.0251.0376'))  # FAILS! [Errno 11001]