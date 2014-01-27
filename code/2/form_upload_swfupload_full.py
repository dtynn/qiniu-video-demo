#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '../')

import os

import tornado
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
import json

from qiniu import conf as qConf, rs as qRs
from qiniu.auth import digest as qDigest

ACCESS_KEY = ''
SECRET_KEY = ''
BUCKET = ''
QINIU_DOMAIN = ''

qConf.ACCESS_KEY = ACCESS_KEY
qConf.SECRET_KEY = SECRET_KEY

#for return & callback
HOST = 'http://'  # http://www.abc.com or http://135.79.24.68
PORT = 51234
selfHost = '%s:%s' % (HOST, PORT)


class UploadHdl(tornado.web.RequestHandler):
    def get(self):
        self.render('form_upload_swfupload_full.html', selfHost=selfHost)
        return


class TokenHdl(tornado.web.RequestHandler):
    def get(self):
        putPolicy = qRs.PutPolicy(scope=BUCKET)
        putPolicy.callbackUrl = '%s/callback' % (selfHost, )
        putPolicy.callbackBody = 'key=$(key)&etag=$(etag)&fsize=$(fsize)&fname=$(x:fname)'
        uptoken = putPolicy.token()
        msg = dict()
        msg['code'] = 0
        msg['type'] = 'token'
        msg['token'] = uptoken
        self.write(json.dumps(msg))
        return


class CallbackHdl(tornado.web.RequestHandler):
    def post(self):
        mac = qDigest.Mac()
        msg = dict()
        key = self.get_argument('key')
        etag = self.get_argument('etag')
        fsize = self.get_argument('fsize')
        fname = self.get_argument('fname')

        #print key, etag, fsize, fname

        auth = str(self.request.headers.get('Authorization'))
        requestBody = self.request.body
        authToken = mac.sign(requestBody)
        valid = auth == 'QBox %s' % (authToken,)
        if valid is not True:
            msg['code'] = 1
            msg['detail'] = 'invalid callback request'
            self.write(json.dumps(msg))
            return

        doDataInsert = True  # 插入数据
        if doDataInsert is not True:
            msg['code'] = 1
            msg['detail'] = 'database error'
            self.write(json.dumps(msg))
            return

        msg['code'] = 0
        msg['key'] = key
        self.write(json.dumps(msg))
        return


settings = dict(
    debug=False,
    template_path='../template/2',
    static_path=os.path.abspath('../static'),
)


urls = [
    (r'/', UploadHdl),
    (r'/token', TokenHdl),
    (r'/callback', CallbackHdl),
]


app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(PORT)
server.start()
tornado.ioloop.IOLoop.instance().start()