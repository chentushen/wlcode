#! /usr/bin/ python
# -*- coding: utf-8 -*-

import os.path
import xml.etree.cElementTree as ET
import socket
import time
from xml.dom import minidom
from os.path import getsize,join,getmtime
import socket
import fcntl
import codecs

# os.path.exists("te")
# os.path.isfile("nothing")
# os.path.isdir("nothing")
def setting_create(dirname):
    settingfile=open(dirname+'/setting.txt','w')
    fcntl.flock(settingfile.fileno(), fcntl.LOCK_EX)
    settingfile.write('dataid:\ndataname:\ndatatype:\ndataext:\ndatapath:\ndatasize:\n'
                      'lastupdate:\ndescription:\nrecordsnum:\nsecuritylevel:\n'
                      'sample:\nsource:\nrefrencestandards:\n'
                      'filenum:\nsharerid:\nkeywords:\nisvalid:\n')
    settingfile.close()

def getdirsize(dir):
    size=0
    for root ,dirs,files in os.walk(dir):
        size+=sum([getsize(join(root,name)) for name in files])
    return size

def setting_set(dirname,dataname):
    settingfile=open(dirname+'/setting.txt','r')
    fcntl.flock(settingfile.fileno(), fcntl.LOCK_EX)
    path=join(dirname,dataname)
    newsetting=''
    for line in settingfile:
        if 'dataid:' in line:
            newsetting+='dataid:'+dirname.split('/')[-1].strip()+'\n'
        elif 'dataname:' in line:
            if '.' in dataname:
                tmp=dataname.split('.')
                newsetting+='dataname:'+('.'.join(tmp[:-1]))[3:]+'\n'
            else:
                newsetting+='dataname:'+dataname[3:]+'\n'
	    #print ('.'.join(tmp[:-1]))[3:]+'\n'
        elif 'datasize:' in line:
            #tarpath=dirname+'/'+dataname+'.tar'
            #if not os.path.exists(tarpath):
            #    os.system('tar czvf {0} {1}'.format(tarpath,path))
            #newsetting+='datasize:'+str('%.1f' % getsize(tarpath)).strip()+'\n'
            if os.path.isdir(path):
                newsetting+='datasize:'+str('%.1f' % getdirsize(path))+'\n'
            else:
                newsetting+='datasize:'+str('%.1f' % getsize(path))+'\n'
        elif 'datapath:' in line:
            addr=socket.gethostbyname(socket.gethostname())
            # addr=socket.ip
            # print addr
            newsetting+='datapath:'+addr+'|'+path+'\n'
        elif 'lastupdate:' in line:
            newsetting+='lastupdate:'+str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(getmtime(path))))+'\n'#更改内容的时间
        else:
            newsetting+=line
    settingfile.close()
    settingfile=open(dirname+'/setting.txt','w')
    fcntl.flock(settingfile.fileno(), fcntl.LOCK_EX)
    # newsetting=unicode(newsetting)
    settingfile.write(newsetting)
    settingfile.close()

def setting_analysis(dirname):
    settingfile=open(dirname+'/setting.txt','r')
    fcntl.flock(settingfile.fileno(), fcntl.LOCK_EX)
    settingdict={}
    for line in settingfile:
        line=line.replace('\n','')
        coindex=line.index(':')
        settingdict[line[:coindex]]=line[coindex+1:]
    settingfile.close()
    return settingdict

def xml_create(dirname):
    settingdict=setting_analysis(dirname)
    doc = minidom.Document()
    rootNode = doc.createElement('dataset')
    doc.appendChild(rootNode)
    for key,value in settingdict.items():
        newnode=doc.createElement(key)
        newnode.appendChild(doc.createTextNode(value))
        rootNode.appendChild(newnode)
    f = open(dirname+'/readme.xml','w')
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    # doc=doc.encoding('utf-8')
    doc.writexml(f)
    f.close()

def xml_analysis(dirname):
    xmlstrfile=open(dirname+'/readme.xml','r')
    fcntl.flock(xmlstrfile.fileno(), fcntl.LOCK_EX)
    xmlstr=xmlstrfile.read()
    xmlstrfile.close()
    xmlItem={'dataid':'','dataname':'','datatype':'','dataext':'','datapath':'','datasize':'','lastupdate':'',
             'description':'','recordsnum':'','securitylevel':'','sample':'','source':'',
             'refrencestandards':'','filenum':'','sharerid':'','keywords':'','isvalid':''}
    root = ET.fromstring(xmlstr)
    for key in xmlItem.keys():
        try:
            xmlItem[key]=root.find(key).text.replace('\n','').strip()
        except:
            xmlItem[key]=''
    return xmlItem

def cmp_xmlandset(dirname):
    settingdict=setting_analysis(dirname)
    xmldict=xml_analysis(dirname)
    mark=True
    for key in settingdict.keys():
        s1=str(settingdict[key]).decode('utf-8')
        tmp=xmldict[key]
        s2=tmp
        if s1!=s2:
            mark=False
            break
    return mark

def dictostr(thedict):
    data=''
    for key,value in thedict.iteritems():
        data+="'%s':'%s'," % (key,value)
    data='{'+data[:-1]+'}'
    return data

def connectSer(cmd,xml):
    print '连接...'
    global serverhost,serverport
    # bufsize = 1024
    addr = (serverhost,serverport)

    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(addr)
    datadict={'cmd':cmd,'content':xml}
    # datadict="{'id':'111','name':'wl'}"
    client.send(dictostr(datadict))
    client.close()

def scan_buffer(cmdname):
    global bufpath
    for xmlname in os.listdir(bufpath+'/'+cmdname):
        if '~' in xmlname:
            continue
        xmlfile=open(bufpath+'/'+cmdname+'/'+xmlname,'r')
        fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
        xmlstr=xmlfile.read()
        xmlfile.close()
        try:
            if cmdname=='set':
                connectSer(cmddict['data_set'],xmlstr)
            elif cmdname=='update':
                connectSer(cmddict['xml_update'],xmlstr)
            os.system("rm -f '%s/%s/%s'" % (bufpath,cmdname,xmlname))
        except:
            print 'buffer连接失败'
            pass

def configParameter(paName):
    pa=None
    if os.path.exists('config'):
        with open('config') as f:
            for line in f:
                if paName+':' in line:
                    pa=line.replace('\n','').split(':')[1]
                    break
    else:
        f=open('config','w')
        f.write('storageID:001\nnewDataID:0010000001')
        return pa
    return pa

def scan_file(datadir):
    global cmddict
    mark_setting=False
    mark_xml=False
    mark_data=False
    dataname=''
    # print datadir
    for filename in os.listdir(datadir):
        if '~' not in filename:
            # print os.path.join(datadir,filename)
            if 'setting.txt'==filename:
                mark_setting=True
            elif 'readme.xml'==filename:
                mark_xml=True
            elif '96_' == filename[:3]:
                mark_data=True
                dataname=filename

    dataid=datadir.split('/')[-1]
    if mark_setting==False:
        print '无setting文件，正生成setting文件'
        setting_create(datadir)
        if mark_data==True:
            setting_set(datadir,dataname)
            xml_create(datadir)
            #connect to server CMD_DATA_SET
            xmlfile=open(datadir+'/readme.xml','r')
            fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
            xmlstr=xmlfile.read()
            xmlfile.close()
            try:
                connectSer(cmddict['data_set'],xmlstr)
            except:
                print '连接失败'
                xmlfile=open(bufpath+'/set/'+dataid,'w')
                fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
                xmlfile.write(xmlstr)
                xmlfile.close()
    else:
        setting_set(datadir,dataname)
        if (mark_xml==False and mark_data==True) or \
            (mark_xml==True and cmp_xmlandset(datadir)==False):
            xml_create(datadir)
            #connect to server CMD_XML_DATA
            xmlfile=open(datadir+'/readme.xml','r')
            fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
            xmlstr=xmlfile.read()
            xmlfile.close()
            try:
                connectSer(cmddict['xml_update'],xmlstr)
            except:
                xmlfile=open(bufpath+'/update/'+dataid,'w')
                fcntl.flock(xmlfile.fileno(), fcntl.LOCK_EX)
                xmlfile.write(xmlstr)
                xmlfile.close()


datapath='/export/storage6d5/datasets'#绝对路径
bufpath='/home/dataman/wlAgent/wenlibuffer'#绝对路径
serverhost = '10.141.208.63'
serverport = 9696
if __name__ == '__main__':
    cmddict={'ack':0x00000005,'nak':0x0000000F,'time_set':0x00010001,\
         'data_set':0x00020001,'xml_update':0x00020010,'xml_data':0x00020100}
    #'/export/storage6d5/datasets'

    # scan_file(datapath)
    while True:
        for dataid in os.listdir(datapath):
            storageID = configParameter('storageID')
            if storageID == dataid[:3] and len(dataid) == 10:  # 是否为新数据
                if '~' not in dataid:
                    # os.path.join(datapath,dataid)
                    scan_file(datapath+'/'+dataid)
                    scan_buffer('set')
                    scan_buffer('update')
            else:
                filepath = datapath + '/' + dataid  # 新数据位置
                newDataID = configParameter('newDataID')
                newDataDir = datapath + '/' + newDataID  # 给新数据件文件夹后的新数据的路径
                os.mkdir(newDataDir)

                os.system('mv {0} {1}'.format(filepath, newDataDir))  # 剪切
                # 重命名
                os.system('mv {0} {1}'.format(newDataDir + '/' +dataid, newDataDir + '/96_' + dataid))

                # 更新newDataID
                temp = int(newDataID[3:]) + 1
                print temp
                if len(str(temp)) < 8:
                    newDataID = newDataID[:3] + '0' * (7 - len(str(temp))) + str(temp)
                print newDataID
                s = ''
                with open('config', 'r') as f:
                    for line in f:
                        if 'newDataID:' in line:
                            s += 'newDataID:' + newDataID + '\n'
                        else:
                            s += line
                with open('config', 'w') as f:
                    f.write(s)

        time.sleep(5)
