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


class PlayerHdl(tornado.web.RequestHandler):
    def get(self):
        self.render('player_converted.html')
        return


PORT = 51234

settings = dict(
    debug=False,
    template_path='../template/3',
    static_path=os.path.abspath('../static')
)


urls = [
    (r'/', PlayerHdl),
]


app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(PORT)
server.start()
tornado.ioloop.IOLoop.instance().start()