#!/usr/bin/python

import socket

def ClientTest():
    client = socket.create_connection(('127.0.0.1', 50000), 2)
    data = 'test'
    client.send(data)
    data = client.recv(1024)
    print data
    client.close()

def action():
    print 'test'

d = {}
d[1] = lambda: action()

d[1]()

