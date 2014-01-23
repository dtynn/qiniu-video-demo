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
    putPolicy = qRs.PutPolicy(scope=BUCKET)
    uptoken = putPolicy.token()

    filePath = '../files/test.jpg'

    key = 'upload_put.jpg'

    f = open(filePath, 'rb')
    data = f.read()

    #上传结果
    ret, err = qIo.put(uptoken, key, data)
    print ret
    print err
    print 'http://%s/%s' % (QINIU_DOMAIN, key)