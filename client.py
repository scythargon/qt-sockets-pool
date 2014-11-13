#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import sys

if len(sys.argv)<2:
    print 'provide the address as command argument please'
    sys.exit(1)


def recvall(sock):
    data = ""
    part = None
    while part != "":
        part = sock.recv(4096)
        data+=part
    return data

sock = socket.socket()
sock.connect(('localhost', 8002))
sock.send(sys.argv[1])

data = recvall(sock)
sock.close()

print data