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
from tornado.httpclient import HTTPError
import json

from qiniu import conf as qConf, rs as qRs
from qiniu.auth import digest as qDigest
from dbs import mData
import time

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

dbPath = 'qvideo.db'
miniData = mData(dbPath)


class TokenHdl(tornado.web.RequestHandler):
    def get(self):
        putPolicy = qRs.PutPolicy(scope=BUCKET)
        putPolicy.callbackUrl = '%s/callback' % (selfHost, )
        putPolicy.callbackBody = 'key=$(key)&etag=$(etag)&fsize=$(fsize)&fname=$(x:fname)&persistentId=$(persistentId)'
        putPolicy.persistentOps = 'avthumb/mp4'
        putPolicy.persistentNotifyUrl = '%s/notify' % (selfHost,)
        uptoken = putPolicy.token()
        msg = dict()
        msg['code'] = 0
        msg['type'] = 'token'
        msg['token'] = uptoken
        self.write(json.dumps(msg))
        return


class CallbackHdl(tornado.web.RequestHandler):
    def post(self):
        self.set_header('Content-Type', 'application/json')
        mac = qDigest.Mac()
        msg = dict()
        uid = 0
        key = self.get_argument('key')
        etag = self.get_argument('etag')
        fsize = self.get_argument('fsize')
        fname = self.get_argument('fname')
        persistentId = self.get_argument('persistentId')

        #print key, etag, fsize, fname

        auth = str(self.request.headers.get('Authorization'))
        requestBody = self.request.body
        authToken = mac.sign('/callback\n%s' % (requestBody,))
        valid = auth == 'QBox %s' % (authToken,)
        if valid is not True:
            msg['code'] = 1
            msg['detail'] = 'invalid callback request'
            self.write(json.dumps(msg))
            return

        doDataInsert = miniData.VideoAdd(uid, etag, fname, fsize, persistentId)  # 插入数据
        if doDataInsert is not True:
            msg['code'] = 1
            msg['detail'] = 'database error'
            self.write(json.dumps(msg))
            return

        msg['code'] = 0
        msg['key'] = key
        msg['persistentId'] = persistentId
        self.write(json.dumps(msg))
        return


class NotifyHdl(tornado.web.RequestHandler):
    def post(self):
        mimeType = 'application/json'
        if self.request.headers.get('Content-Type', '') == mimeType:
            data = self.request.body
            dataObj = json.loads(data)
            pid = dataObj.get('id')
            status = dataObj.get('code')
            if pid:
                miniData.VideoUpdateOpsStatus(pid, status, data)
        return


class PageUploadHdl(tornado.web.RequestHandler):
    def get(self):
        self.render('video_demo_upload.html', selfHost=selfHost)
        return


class PageListHdl(tornado.web.RequestHandler):
    def get(self):
        videoList = miniData.VideoListAll()
        status = {
            -1: '等待处理',
            1: '等待处理',
            2: '正在处理',
            3: '处理失败',
            4: '回调失败',
        }
        self.render('video_demo_list.html', vList=videoList, status=status, time=time)
        return


class PagePlayerHdl(tornado.web.RequestHandler):
    def get(self):
        try:
            vid = int(self.get_argument('vid'))
        except (HTTPError, ValueError, TypeError):
            self.write('404')
            return
        res = miniData.VideoGet(vid)
        if res:
            etag = res['hash']
            self.render('video_demo_player.html', domain=QINIU_DOMAIN, etag=etag)
            return
        self.write('404')
        return


settings = dict(
    debug=False,
    template_path='../template/3',
    static_path=os.path.abspath('../static'),
)


urls = [
    (r'/', PageListHdl),
    (r'/upload', PageUploadHdl),
    (r'/player', PagePlayerHdl),
    (r'/token', TokenHdl),
    (r'/callback', CallbackHdl),
    (r'/notify', NotifyHdl),
]


app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(PORT)
server.start()
tornado.ioloop.IOLoop.instance().start()