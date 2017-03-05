#! /usr/bin/env python
# -*- coding: utf-8 -*-
from SocketServer import (TCPServer as TCP,
                          StreamRequestHandler as SRH,
                          ThreadingMixIn as TMI)
import xml.etree.cElementTree as ET
import MySQLdb
import fcntl
from cmpxmlmysql import xmlsetpath
# try:
#     import xml.etree.cElementTree as ET
# except ImportError:
#     import xml.etree.ElementTree as ET

class Server(TMI, TCP):
    pass

class MyRequestHandler(SRH):#python接收发送的都是字符串，而c是字节流；self.data可能是字符串类型，而self.request.recv()获得的是字节流
    def handle(self):
        # global xmlsetpath
        print '...connected from:', self.client_address
        self.data = self.request.recv(1024)
        # print 'agent:'+self.data
        datadict=eval(self.data)
        # print datadict['content']
        cmd=hex(int(datadict['cmd']))#hex()16进制的字符串
        xmldict=self.xmlanalysis(datadict['content'])
        xmlfile=open(xmlsetpath+'/'+xmldict['dataid'],'w')
        fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
        xmlfile.write(datadict['content'])
        xmlfile.close()
        self.mysql_update(cmd,xmldict)

    def dictostr(self,thedict):
        data=''
        for key,value in thedict.iteritems():
            data+="'%s':'%s'," % (key,value)
        data='{'+data[:-1]+'}'
        return data

    def xmlanalysis(self,xmlstr):
        xmlItem={'dataid':'','dataname':'','datatype':'','dataext':'','datapath':'','datasize':'','lastupdate':'',
                 'description':'','recordsnum':'','securitylevel':'','sample':'','source':'',
                 'refrencestandards':'','filenum':'','sharerid':'','keywords':'','isvalid':''}
        try:
            root = ET.fromstring(xmlstr)
        except Exception, e:
            print "Error:cannot parse "
            return 0
        for key in xmlItem.keys():
            try:
                xmlItem[key]=root.find(key).text.replace('\n','').strip()
            except:
                xmlItem[key]=''
        return xmlItem

    def mysql_update(self,cmd,xmldict):
        # for key in xmldict.keys():
        #     if xmldict[key]=='':
        #         xmldict[key]='null'
        for key in ['recordsnum','securitylevel','filenum','sharerid','isvalid']:
            try:
                xmldict[key]=int(xmldict[key])
            except:
                xmldict[key]=-1
        sql_insert="insert into t_data values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % \
            (xmldict['dataid'],xmldict['dataname'],xmldict['datatype'],xmldict['dataext'],xmldict['datapath'],\
             xmldict['datasize'],xmldict['description'],xmldict['recordsnum'],\
             xmldict['securitylevel'],xmldict['sample'],xmldict['source'],xmldict['refrencestandards'],\
             xmldict['filenum'],xmldict['sharerid'],xmldict['keywords'],xmldict['isvalid'],xmldict['lastupdate'])
        sql_delete="delete from t_data WHERE dataid='%s'" % (xmldict['dataid'])
        conn=MySQLdb.connect(host="10.141.245.162",user="kunchen",passwd="kunchen",db="wenli",charset='utf8')
        cur=conn.cursor()
        # print cmd+','
        if int(cmd,16)==0x20001:
            print 'insert data'
            try:
                cur.execute(sql_insert)
            except:
                cur.execute(sql_delete)
                cur.execute(sql_insert)
        elif int(cmd,16)==0x20010:
            print 'update data'
            cur.execute(sql_delete)
            cur.execute(sql_insert)
        # cur.executemany(sql,list)
        # print 'complete!'
        conn.commit()
        cur.close()
        conn.close()

if __name__ == '__main__':
    cmd={'ack':0x00000005,'nak':0x0000000F,'time_set':0x00010001,\
         'data_set':0x00020001,'xml_update':0x00020010,'xml_data':0x00020100}
    HOST = ''
    PORT = 9696
    ADDR = (HOST, PORT)
    tcpServ = Server(ADDR, MyRequestHandler)
    print 'waiting for connection...'
    tcpServ.serve_forever()