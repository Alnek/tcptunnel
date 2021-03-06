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

read_handler = {}
write_handler = {}

def Accept(socket):
    conn, address = socket.accept()
    print 'accepted: ', address[0], ':', address[1]
    #read_list.append(conn)
    #read_handler[conn.fileno()] = Echo
    CreateTunnel(conn)

def Echo(socket):
    data = socket.recv(BUF_SIZE)
    if len(data) > 0:
        socket.send(data)
    else:
        address = socket.getpeername()
        print 'disconnected: ', address[0], ':', address[1]
        read_list.remove(socket)
        socket.close()        
        
def CreateTunnel(source):
    target = socket.create_connection((TARGET_HOST, TARGET_PORT), 2)
    target.settimeout(None)

    address = target.getpeername()
    print 'connected: ', address[0], ':', address[1]
    
    def disconnect_both():
        address = source.getpeername()
        print 'disconnected: ', address[0], ':', address[1]
        address = target.getpeername()
        print 'disconnected: ', address[0], ':', address[1]

        read_list.remove(source)
        read_list.remove(target)
        
        source.shutdown(socket.SHUT_RDWR)
        source.close()
        target.shutdown(socket.SHUT_RDWR)
        target.close()
    
    def target_read(socket):
        try:
            data = target.recv(BUF_SIZE)
            if len(data) > 0:
                source.send(data)
            else:
                disconnect_both()
        except:
            disconnect_both()

    def source_read(socket):
        try:
            data = source.recv(BUF_SIZE)
            if len(data) > 0:
                target.send(data)
            else:
                disconnect_both()
        except:
            disconnect_both()

    read_handler[source.fileno()] = source_read
    read_handler[target.fileno()] = target_read
    read_list.append(source)
    read_list.append(target)

    return

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

    server.bind((HOST,PORT))
    server.listen(0)
    read_handler[server.fileno()] = Accept

    read_list.append(server)

    while True:
        readable, writable, errored = select.select(read_list, [], [], 1)
        
        if len(readable) == 0:
            continue
            
        for sock in readable:
            read_handler[sock.fileno()](sock)

if __name__ == '__main__':
    main()
