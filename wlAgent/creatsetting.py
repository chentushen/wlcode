#! /usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import time
from os.path import getsize,join,getmtime

def setting_create(dirname):
    settingfile=open(dirname+'/setting.txt','w')
    settingfile.write('dataid:\ndataname:\ndatatype:\ndataext:\ndatapath:\ndatasize:\n'
                      'lastupdate:\ndescription:\nrecordsnum:\nsecuritylevel:\n'
                      'sample:\nsource:\nrefrencestandards:\n'
                      'filenum:\nsharerid:\nkeywords:\nisvalid:\n')
    settingfile.close()

def setting_set(dirname,dataname):
    settingfile=open(dirname+'/setting.txt','r')
    path=join(dirname,dataname)
    newsetting=''
    for line in settingfile:
        if 'dataid:' in line:
            newsetting+='dataid:'+dirname.split('/')[-1].strip()+'\n'
        elif 'dataname:' in line:
            newsetting+='dataname:'+dataname.replace('.tar','').strip()+'\n'
        elif 'datasize:' in line:
            newsetting+='datasize:'+str(getsize(path)).strip()+'\n'
        elif 'datapath:' in line:
            addr=socket.gethostbyname(socket.gethostname())
            newsetting+='datapath:'+addr+'|'+path+'\n'
        elif 'lastupdate:' in line:
            newsetting+='lastupdate:'+str(time.ctime(getmtime(path)))+'\n'#更改内容的时间
        else:
            newsetting+=line
    settingfile.close()
    print newsetting

# if __name__ == '__main__':
#     dirname='/home/chenkun/data/100002'
#     dataname='data.tar'
#     setting_create(dirname)
#     setting_set(dirname,dataname)





