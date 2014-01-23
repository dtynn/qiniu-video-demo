#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '../')

import tornado
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer

from qiniu import conf as qConf, rs as qRs, io as qIo

ACCESS_KEY = ''
SECRET_KEY = ''
BUCKET = ''
QINIU_DOMAIN = ''

qConf.ACCESS_KEY = ACCESS_KEY
qConf.SECRET_KEY = SECRET_KEY


class UploadHdl(tornado.web.RequestHandler):
    def get(self):
        self.render('upload_app.html')
        return

    def post(self):
        files = self.request.files.get('upload_file')
        if not files:
            self.write('no file')
            return
        data = files[0].get('body')
        key = 'upload_app'
        putPolicy = qRs.PutPolicy(scope='%s:%s' % (BUCKET, key))
        uptoken = putPolicy.token()
        print 'up up uploading'
        ret, err = qIo.put(uptoken, key, data)
        if err:
            self.write(err)
        else:
            self.write('http://%s/%s' % (QINIU_DOMAIN, key))
        return


PORT = 51234

settings = dict(
    debug=False,
    template_path='../template/1',
)


urls = [
    (r'/', UploadHdl),
]


app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(PORT)
server.start()
tornado.ioloop.IOLoop.instance().start()