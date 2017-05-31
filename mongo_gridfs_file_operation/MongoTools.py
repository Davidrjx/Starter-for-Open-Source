#coding: utf-8
def getextradatabyid(conndb,filefieldobj,gridfs_id = None):
    '''
    via pymongo interface
    '''
    tmpdict = {}
    if gridfs_id is not None:
        collname = filefieldobj.collection_name + '.files'
        filelength = conndb[collname].find({'_id':gridfs_id}).next()['length']
        tmpdict.setdefault('flength',filelength)
    return tmpdict
