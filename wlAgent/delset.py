import os
path='/export/storage6d5/datasets'
for dir in os.listdir('/export/storage6d5/datasets'):
     #os.system('rm {}'.format(path+'/'+dir+'/setting.txt'))
    for f in os.listdir('/'.join([path,dir])):     
        # if '96_' in f and '.tar' in f:
             # os.system('rm {}'.format('/'.join([path,dir,f]))) 
        print f
