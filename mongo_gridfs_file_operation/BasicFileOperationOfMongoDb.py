#coding: utf-8
'''
Created on Aug,26 2015
@author: jianxin,ren
'''
import os
from time import sleep
from .MongoTools import getextradatabyid


class FileOperationOfMongo(object):
    '''
    Basic App Class of Mongodb GridFS
    '''
    def __init__(self):
        pass
    
    #************#
    #write file-like object , string , datastream to mongodb in non-loop style
    def writefilestomongo(self,collinstance,file_fs_data='Mustupdate',**kwargs):
        iscreate = False   #whether grid_file is create
        gridfsproxy = None
        try:
            #solution one
            #conn_database = conn_instance[mongodb_name]
            #gridfs_instance = gridfs.GridFS(conn_database,collection=kwargs['log_collection_name'])
            #fsid = gridfs_instance.put(data,filename=kwargs['log_file_name'])
            
            #solution two
            gridfsproxy = collinstance['file_fs_data']
            if 'content_type' not in kwargs:
                gridfsproxy.put(file_fs_data)
            else:
                gridfsproxy.put(file_fs_data,content_type=kwargs.get('content_type',None))
            
            for fieldnm , fieldval in kwargs.items():
                if fieldnm is not 'content_type':
                    collinstance[fieldnm] = fieldval
            collinstance.save() 
            
            if gridfsproxy:
                iscreate = True
            return iscreate , gridfsproxy
        except Exception as err:
            print 'GridFs ERROR:%s'%err
            return iscreate , gridfsproxy
     
    #************#
    #currently fit with file upload operation at front-end . write file chunk to mongodb in loop style
    def writefilechunktomongo(self,collinstance,uploadedfileobj,**kwargs):
        gridfsproxy = collinstance['file_fs_data']
        if 'content_type' not in kwargs:
            gridfsproxy.new_file()
        else:
            gridfsproxy.new_file(content_type=kwargs.get('content_type',None))
            
        for chunk in uploadedfileobj.chunks():
            gridfsproxy.write(chunk)
        
        sleep(1)
        gridfsproxy.close()
        
        for fieldnm , fieldval in kwargs.items():
            if fieldnm is not 'content_type':
                collinstance[fieldnm] = fieldval
        #gridfileobj.close()
        collinstance.save() 
           
    #************#
    #currently fit with .pcap or .pcapng file storage in rdnet business
    def writefileitertomongo(self,collinstance,fpath,storestyle=0,chksize=1024*1024,**kwargs):
        assert collinstance
        if os.path.exists(fpath) and os.path.isfile(fpath):
            gridfsproxy = collinstance['file_fs_data']
            fd = open(fpath,'rb') #use built-in 
            isexcept = False
            
            if storestyle == 0:#mainly for larger file
                print '0'
                if 'content_type' not in kwargs:
                    gridfsproxy.new_file()
                else:
                    gridfsproxy.new_file(content_type=kwargs.get('content_type',None))
        
                try:
                    while True:
                        fchunk = fd.read(chksize)
                        if not fchunk:
                            break
                        gridfsproxy.write(fchunk)
                except:
                    isexcept = True

            else:#general file,by default
                try:
                    gridfsproxy.put(fd)
                except:
                    isexcept = True

            #finally,save data into Document class
            fd.flush()
            fd.close()
            gridfsproxy.close()
            if not isexcept:
                collinstance.save()
                
        else:
            print 'please specify file directory and filename'
             
    #************#
    #get file list by file-name-field     
    def getfilesbyfilenamekey(self,collclass,file_name_field=None):
        gffilelist = []
        if file_name_field:
            for perdoc in collclass.objects.only(file_name_field).all():
                gffilelist.append(perdoc[file_name_field])
            return gffilelist    
        else:
            return gffilelist
    
    #************#   
    #get a specified file by grid-file-id
    #para:_conndb (optional).if not None,file length returned
    def getfilesbyfileid(self,collclass,gfile_query_id,gfile_nm_key='file_name_field',_conndb=None):
        try:
            extradata = {}
            docres = collclass.objects(file_fs_data=gfile_query_id).only(gfile_nm_key).first()
            
            if _conndb:
                if hasattr(collclass, 'file_fs_data'):
                    filefieldobj = getattr(collclass, 'file_fs_data')
                    extradata = getextradatabyid(_conndb,filefieldobj,gridfs_id=gfile_query_id).copy()
                return docres[gfile_nm_key] , extradata
            else:
                return docres[gfile_nm_key]
        except Exception as err:
            print 'Get File-Name By_id  ERROR:%s'%err
            return None , None
 

#*****************************************************************# 
#separate module,non-class,fit wit front-end storage demand
def uploadtomongohandler(collinstance,uploadedfile,**kwargs):
    fileoperobj = FileOperationOfMongo() 
    kwargs.setdefault('content_type',uploadedfile.content_type)
    if uploadedfile.multiple_chunks():#file size bigger than 2.5MB
        fileoperobj.writefilechunktomongo(collinstance, uploadedfile, **kwargs)
    else:
        fileoperobj.writefilestomongo(collinstance, file_fs_data=uploadedfile.read(), **kwargs)
    

    