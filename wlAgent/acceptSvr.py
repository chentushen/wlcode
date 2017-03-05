#! /usr/bin/env python
# -*- codi
# ng: utf-8 -*-
from _socket import *
import xml.etree.cElementTree as ET
import os,fcntl
from scanfiles import datapath

def xml_analysis(xml):
    xmlItem={'dataid':'','dataname':'','datatype':'','dataext':'','datapath':'','datasize':'','lastupdate':'',
             'description':'','recordsnum':'','securitylevel':'','sample':'','source':'',
             'refrencestandards':'','filenum':'','sharerid':'','keywords':'','isvalid':''}
    root = ET.fromstring(xml)
    for key in xmlItem.keys():
        try:
            xmlItem[key]=root.find(key).text.replace('\n','').strip()
        except:
            xmlItem[key]=''
    return xmlItem

if __name__ == '__main__':
    Host=''
    PORT=50007
    BUFSIZE=1024
    ADDR=(Host,PORT)

    agentSocket=socket(AF_INET,SOCK_STREAM)
    agentSocket.bind(ADDR)
    agentSocket.listen(1)
    cmddict={'ack':0x00000005,'nak':0x0000000F,'time_set':0x00010001,\
         'data_set':0x00020001,'xml_update':0x00020010,'xml_data':0x00020100}

    while True:
        print 'wait for svr...'
        svrSocket,addr=agentSocket.accept()
        print addr
        data=svrSocket.recv(BUFSIZE)
        print data
        datadict=eval(data.replace('\n',''))
        cmd=hex(int(datadict['cmd']))
        if int(cmd,16)==cmddict['xml_data']:
            xmldict=xml_analysis(datadict['content'])
            dataid=xmldict['dataid']
            settingfile=open(datapath+'/'+dataid+'/setting.txt','w')
            fcntl.flock(settingfile.fileno(), fcntl.LOCK_EX)
            for key,value in xmldict.items():
                settingfile.write(key.encode('utf-8')+':'+value.encode('utf-8')+'\n')
            settingfile.close()
            xmlfile=open(datapath+'/'+dataid+'/readme.xml','w')
            fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
            xmlfile.write(datadict['content'])
            xmlfile.close()
        elif cmd==cmddict['time_set']:
            os.system("date -s '%s'" % datadict['content'].strip())
        svrSocket.close()
    agentSocket.close()
