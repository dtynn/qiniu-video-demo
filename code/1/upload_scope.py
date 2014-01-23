#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '../')

from qiniu import conf as qConf, rs as qRs, io as qIo

ACCESS_KEY = ''
SECRET_KEY = ''
BUCKET = ''
QINIU_DOMAIN = ''

qConf.ACCESS_KEY = ACCESS_KEY
qConf.SECRET_KEY = SECRET_KEY

if __name__ == '__main__':
    key = 'upload_scope.jpg'
    putPolicy = qRs.PutPolicy(scope='%s:%s' % (BUCKET, key))
    uptoken = putPolicy.token()

    filePath = '../files/test.jpg'
    filePath2 = '../files/test.mp4'
    key = 'upload_scope.jpg'

    #file exists
    ret, err = qIo.put_file(uptoken, key, filePath)
    ret, err = qIo.put_file(uptoken, key, filePath2)
    print ret
    print err