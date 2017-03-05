#! /usr/bin/env python
# -*- coding:utf-8 -*-
import xml.etree.cElementTree as ET
from socket import*
import MySQLdb
from xml.dom import minidom
import os,time,fcntl

def xmlanalysis(xmlstr):
    if xmlstr.strip()=='':return 0
    xmlItem={'dataid':'','dataname':'','datatype':'','dataext':'','datapath':'','datasize':'','lastupdate':'',
             'description':'','recordsnum':'','securitylevel':'','sample':'','source':'',
             'refrencestandards':'','filenum':'','sharerid':'','keywords':'','isvalid':''}
    #root = ET.fromstring(xmlstr)

    try:
        root = ET.fromstring(xmlstr)
    except Exception, e:
        print "Error:cannot parse ",xmlstr,"xxxxxxxxxxxxxxx"
        # sys.exit(1)
        return 0
    for key in xmlItem.keys():
        try:
            xmlItem[key]=root.find(key).text.replace('\n','').strip()
        except:
            xmlItem[key]=''
    return xmlItem

def xml_update(xmldict):
    # print xmldict
    doc=minidom.Document()
    rootNode=doc.createElement('dataset')
    doc.appendChild(rootNode)
    for key,value in xmldict.items():
        newNode=doc.createElement(key)
        if isinstance(value,(int,long,float)):
            newNode.appendChild(doc.createTextNode(str(value)))
        else:
            newNode.appendChild(doc.createTextNode(value))
        rootNode.appendChild(newNode)
    return doc.toprettyxml()

def dictostr(thedict):
    data=''
    for key,value in thedict.iteritems():
        data+="'%s':'%s'," % (key,value)
    data='{'+data[:-1]+'}'
    return data

def connectAgent(host,cmd,content):
    port = 50007
    # bufsize = 1024
    addr = (host,port)
    client = socket(AF_INET,SOCK_STREAM)
    client.connect(addr)
    datadict={'cmd':cmd,'content':content}
    # datadict="{'id':'111','name':'wl'}"
    client.send(dictostr(datadict))
    client.close()

def scan_buffer():
    print '正在扫描buffer文件夹......'
    global xmlsetpath,xmlbufpath
    for xmlname in os.listdir(xmlbufpath):
        if '~' in xmlname:
            continue
        xmlfile=open(xmlbufpath+'/'+xmlname,'r')
        fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
        xmlstr=xmlfile.read()
        xmldict=xmlanalysis(xmlstr)
        xmlfile.close()
        host=xmldict['datapath'].split('|')[0]
        try:
            connectAgent(host,cmddict['xml_data'],xmlstr)
            os.system("rm -f '%s/%s'" % (xmlbufpath,xmlname))
            print 'buffer中的',xmlname,'传送成功!'
        except:
            print 'buffer中的xml文件传送Agent失败!'
    print 'buffer文件夹扫描结束'

xmlsetpath = '/home/chenkun/wlServer/xmlset'
xmlbufpath = '/home/chenkun/wlServer/buffer'
if __name__ == '__main__':
    cmddict={'ack':0x00000005,'nak':0x0000000F,'time_set':0x00010001,\
             'data_set':0x00020001,'xml_update':0x00020010,'xml_data':0x00020100}
    thedate=time.strftime("%Y:%m:%d",time.localtime())
    while True:
        for xmlid in os.listdir(xmlsetpath):
            print xmlid,'--------------------------'
            if '~' in xmlid:
                continue
            xmlfile=open(xmlsetpath+'/'+xmlid,'r')
            fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
            #print xmlfile.read(),'**********'
            xmldict=xmlanalysis(xmlfile.read())
	    if xmldict==0:
               # print xmlid,'xml读取失败...'
                continue
            for key in xmldict.keys():
                if isinstance(xmldict[key],(int,float,long)):
                    xmldict[key]=str(xmldict[key]).encode('utf-8')
                else:
                    xmldict[key]=xmldict[key].encode('utf-8')
            xmlfile.close()
            conn=MySQLdb.connect(host="10.141.245.162",user="kunchen",passwd="kunchen",db="wenli",charset='utf8')
            cur=conn.cursor()
            #print xmldict,'-----------------------'
            sql_sel="select * from t_data where DataID={0}".format(xmldict['dataid'],)
            cur.execute(sql_sel)
            result=cur.fetchone()
            mysqldict={'dataid':result[0],'dataname':result[1],'datatype':result[2],'dataext':result[3],'datapath':result[4],\
                       'datasize':result[5],'description':result[6],'recordsnum':result[7],'securitylevel':result[8],\
                       'sample':result[9],'source':result[10],'refrencestandards':result[11],'filenum':result[12],\
                       'sharerid':result[13],'keywords':result[14],'isvalid':result[15],'lastupdate':result[16]}
            
            # print mysqldict
            for key in mysqldict.keys():
                if isinstance(mysqldict[key],(long,float,int)):
                    mysqldict[key]=str(mysqldict[key]).encode('utf-8')
                else:
                    mysqldict[key]=mysqldict[key].encode('utf-8')
            mark=True
            for key in mysqldict.keys():
                if xmldict[key]!=mysqldict[key]:
                    mark=False
                    break
            if mark==False:
                host=mysqldict['datapath'].split('|')[0]
                # print host
                newxml=xml_update(mysqldict)
                print 'newxml:',newxml
                xmlfile=open(xmlsetpath+'/'+xmldict['dataid'],'w')
                fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
                xmlfile.write(newxml)
                # print newxml
                try:
                    connectAgent(host,cmddict['xml_data'],newxml)
                except:
                    #write newxml into buffer
                    bufferfile=open(xmlbufpath+'/'+xmldict['dataid'],'w')
                    fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
                    bufferfile.write(newxml.encode('utf-8'))
                    bufferfile.close()
                xmlfile.close()
        scan_buffer()
        time.sleep(5)

    # if time.strftime("%Y-%m-%d",time.localtime())!=thedate:
    #     for agenthost in [host1,]:
    #         connectAgent(agenthost,cmddict['time_set'],time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
    #         thedate=time.strftime("%Y-%m-%d",time.localtime())

