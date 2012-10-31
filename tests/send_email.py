cmd_pre = """EHLO flashpad
MAIL FROM: foo@bar.com
RCPT TO: foo@bar.com
RCPT TO: console
DATA
"""
mailtext = open("mail4","r").read()

cmd_post = "QUIT"

host="localhost"
mode=0
import socket
from sys import argv
if len(argv) != 2:
    raise SystemExit("Usage: %s <port>" % argv[0])
try:
    port = int(argv[1])
except ValueError:
    raise SystemExit("Usage: %s <port>" % argv[0])



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

alltext = cmd_pre + mailtext + "\n.\n" + cmd_post

for l in alltext.split("\n"):
    s.sendall(l+"\r\n")
    if l == ".": mode = 0 # after email content
    print '>>', l
    if mode == 0:
	data = s.recv(1024)
	print data
	if "354" in data: # after DATA
	    mode = 1
    
    
s.close()



