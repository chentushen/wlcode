#! /usr/bin/env python
# -*- coding: utf-8 -*-
from socket import*
from scanfiles import serverhost,serverport

def dictostr(thedict):
    data=''
    for key,value in thedict.iteritems():
        data+="'%s':'%s'," % (key,value)
    data='{'+data[:-1]+'}'
    return data

def connectSer(cmd,xml):
    # bufsize = 1024
    addr = (serverhost,serverport)
    client = socket(AF_INET,SOCK_STREAM)
    client.connect(addr)
    datadict={'cmd':cmd,'content':dictostr(xml)}
    # datadict="{'id':'111','name':'wl'}"
    client.send(datadict)
    client.close()

# while True:
    # data = raw_input('agent:')
    # if not data or data=='exit':
    #     break
    # client.send('%s\r\n' % data)
    # data = client.recv(bufsize)
    # if not data:
    #     break
    # print 'server:'+data.strip()
# client.close()

