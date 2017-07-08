import socket
import select
import signal
import sys
import http.client

from config import *

action_list = []

def signal_handler(signal, frame):
	print('Interrupt!!!')
	for action in action_list:
		action()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def onExit(action):
	action_list.append(action)

def main():

	conn = http.client.HTTPConnection(PROXY_HOST, PROXY_PORT)
	#conn.set_tunnel('www.python.org', 80)
	#conn.set_tunnel('ping.eu', 80)
	conn.set_tunnel('www.example.com', 80)
	conn.request('GET','/')

	response = conn.getresponse()
	print(response.status, response.reason)
	for h in response.getheaders():
		print(h)
	print(response.read())

	sys.exit(0)

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	onExit(lambda:( print('Close socket'), server.close()))

	server.bind((HOST,PORT))
	server.listen(0)

	read_list = [server]

	while True:
		readable, writable, errored = select.select(read_list, [], [], 1)
		
		if len(readable) == 0:
			continue
			
		for sock in readable:
			if sock is server:
				conn, address = server.accept()
				print('connected: ', address[0], ':', address[1])
				read_list.append(conn)
			else:
				data = sock.recv(BUF_SIZE)
				if len(data) > 0:
					sock.send(data)
				else:
					address = sock.getpeername()
					print('disconnected: ', address[0], ':', address[1])
					sock.close()
					read_list.remove(sock)

if __name__ == '__main__':
	main()
