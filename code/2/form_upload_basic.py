#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '../')

import tornado
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer

from qiniu import conf as qConf, rs as qRs

ACCESS_KEY = ''
SECRET_KEY = ''
BUCKET = ''
QINIU_DOMAIN = ''

qConf.ACCESS_KEY = ACCESS_KEY
qConf.SECRET_KEY = SECRET_KEY


class UploadHdl(tornado.web.RequestHandler):
    def get(self):
        putPolicy = qRs.PutPolicy(scope=BUCKET)
        uptoken = putPolicy.token()
        self.render('form_upload_basic.html', token=uptoken)
        return


PORT = 51234

settings = dict(
    debug=False,
    template_path='../template/2',
)


urls = [
    (r'/', UploadHdl),
]


app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(PORT)
server.start()
tornado.ioloop.IOLoop.instance().start()