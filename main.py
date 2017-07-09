#!/usr/bin/python

import socket
import select
import signal
import sys
import httplib

from config import *

action_list = []

def signal_handler(signal, frame):
    print 'Interrupt!!!'
    for action in action_list:
        action()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def onExit(action):
    action_list.append(action)

read_list = []
write_list = []
ex_list = []

read_handler = {}
write_handler = {}

def Accept(socket):
    conn, address = socket.accept()
    print 'connected: ', address[0], ':', address[1]
    read_list.append(conn)
    read_handler[conn.fileno()] = Echo

def Echo(socket):
    data = socket.recv(BUF_SIZE)
    if len(data) > 0:
        socket.send(data)
    else:
        address = socket.getpeername()
        print 'disconnected: ', address[0], ':', address[1]
        socket.close()
        read_list.remove(socket)

def main():
#    conn = httplib.HTTPConnection(PROXY_HOST, PROXY_PORT)
#    conn.set_tunnel('www.python.org', 80)
#    conn.set_tunnel('ping.eu', 80)
#    conn.set_tunnel('www.example.com', 80)
#    conn.request('GET','/')
#
#    response = conn.getresponse()
#    print response.status, response.reason
#    for h in response.getheaders():
#        print h
#    print response.read()
#
#    sys.exit(0)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    onExit(lambda:( server.close()))

    #target = socket.create_connection((TARGET_HOST, TARGET_PORT), 2)
    #target.settimeout(None)

    server.bind((HOST,PORT))
    server.listen(0)
    read_handler[server.fileno()] = Accept

    read_list.append(server)

    while True:
        readable, writable, errored = select.select(read_list, write_list, ex_list, 1)
        
        if len(readable) == 0:
            continue
            
        for sock in readable:
            read_handler[sock.fileno()](sock)

if __name__ == '__main__':
    main()
