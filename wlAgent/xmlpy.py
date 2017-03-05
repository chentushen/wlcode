#! /usr/bin/env python
# -*- coding: utf-8 -*-
from xml.dom import minidom
import xml.etree.cElementTree as ET
def setting_analysis(dirname):
    settingfile=open(dirname+'/setting.txt','r')
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
    # print doc.toprettyxml()
    f = file(dirname+'/book.xml','w')
    doc.writexml(f)
    f.close()

def xml_analysis(dirname):
    xmlstr=open(dirname+'/readme.xml','r')
    xmlItem={'dataid':'','dataname':'','datatype':'','datapath':'','datasize':'','lastupdate':'',
             'description':'','recordsnum':'','securitylevel':'','sample':'','source':'',
             'refrencestandards':'','filenum':'','sharerid':'','keywords':'','isvalid':''}
    try:
        root = ET.fromstring(xmlstr)
    except Exception, e:
        print "Error:cannot parse "
        # sys.exit(1)
        return 0
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
        if settingdict[key]!=xmldict[key]:
            mark=False
            break
    return mark

# xml_create('/home/chenkun/data/100002')
# f = file("book.xml","w")
# doc.writexml(f)
# f.close()