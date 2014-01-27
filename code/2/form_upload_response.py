#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '../')

import tornado
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from base64 import urlsafe_b64decode as b64d
import urllib
import json

from qiniu import conf as qConf, rs as qRs

ACCESS_KEY = ''
SECRET_KEY = ''
BUCKET = ''
QINIU_DOMAIN = ''

#for return & callback
HOST = 'http://'  # http://www.abc.com or http://135.79.24.68
PORT = 51234
selfHost = '%s:%s' % (HOST, PORT)

qConf.ACCESS_KEY = ACCESS_KEY
qConf.SECRET_KEY = SECRET_KEY


class UploadHdl(tornado.web.RequestHandler):
    def get(self):
        returnUrl = '%s/return' % (selfHost,)
        returnBody = '{"key": $(key), "mimeType": $(mimeType)}'

        callbackUrl = '%s/callback' % (selfHost,)
        callbackBody = 'key=$(key)&mimeType=$(mimeType)'

        #只设置returnBody
        putPolicy1 = qRs.PutPolicy(scope=BUCKET)
        putPolicy1.returnBody = returnBody
        uptoken1 = putPolicy1.token()

        #只设置returnUrl
        putPolicy2 = qRs.PutPolicy(scope=BUCKET)
        putPolicy2.returnUrl = returnUrl
        uptoken2 = putPolicy2.token()

        #设置returnUrl和returnBody
        putPolicy3 = qRs.PutPolicy(scope=BUCKET)
        putPolicy3.returnUrl = returnUrl
        putPolicy3.returnBody = returnBody
        uptoken3 = putPolicy3.token()

        #设置callback和callbackBody
        putPolicy4 = qRs.PutPolicy(scope=BUCKET)
        putPolicy4.callbackUrl = callbackUrl
        putPolicy4.callbackBody = callbackBody
        uptoken4 = putPolicy4.token()

        self.render('form_upload_response.html', token1=uptoken1, token2=uptoken2, token3=uptoken3,
                    token4=uptoken4)
        return


class ReturnHdl(tornado.web.RequestHandler):
    def get(self):
        uploadRet = str(self.get_argument('upload_ret', ''))
        if not uploadRet:
            errCode = str(self.get_argument('code', ''))
            errDetail = str(self.get_argument('error', 'something error'))
            msg = dict()
            msg['type'] = 'error'
            msg['code'] = errCode
            msg['detail'] = urllib.unquote(errDetail)
            self.write(json.dumps(msg))
            return
        msg = b64d(uploadRet)
        self.write(msg)
        return


class CallbackHdl(tornado.web.RequestHandler):
    def post(self):
        key = self.get_argument('key')
        mimeType = self.get_argument('mimeType')
        msg = dict()
        msg['type'] = 'callback'
        msg['code'] = 0
        msg['key'] = key
        msg['mimeType'] = mimeType
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(msg))
        return


settings = dict(
    debug=False,
    template_path='../template/2',
)


urls = [
    (r'/', UploadHdl),
    (r'/return', ReturnHdl),
    (r'/callback', CallbackHdl),
]


app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(PORT)
server.start()
tornado.ioloop.IOLoop.instance().start()