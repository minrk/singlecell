# coding: utf-8
"""A simple webapp with a single IPython Notebook Cell

Authors:

* Min RK
"""
#-----------------------------------------------------------------------------
#  Copyright (C) 2013  Min RK
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# stdlib
import logging
import os

# Install the pyzmq ioloop. This has to be done before anything else from
# tornado is imported.
from zmq.eventloop import ioloop
ioloop.install()

from tornado import httpserver
from tornado import web

# IPython
from IPython.kernel.multikernelmanager import MultiKernelManager

from IPython.frontend.html.notebook.handlers import (
    KernelHandler, KernelActionHandler,
    IOPubHandler, ShellHandler,
)
from IPython.frontend.html.notebook.notebookapp import (
    _kernel_action_regex,
)

#-----------------------------------------------------------------------------
# The Tornado web application
#-----------------------------------------------------------------------------

_kernel_id_regex = r"(?P<kernel_id>\w+)"

class DummyIPythonApp(object):
    """It's dumb that we need this"""
    websocket_host = 'localhost:8000'


class IndexHandler(web.RequestHandler):
    def get(self):
        return self.render('index.html')

class SingleCellHandler(web.RequestHandler):
    def get(self):
        return self.render('singlecell.html')

class BesselHandler(web.RequestHandler):
    def get(self):
        return self.render('besselfunctions.html')


class WebApp(web.Application):

    def __init__(self, kernel_manager, kernel_id, log):
        handlers = [
            (r"/", IndexHandler),
            (r"/singlecell", SingleCellHandler),
            (r"/bessel", BesselHandler),
            (r"/kernels/%s" % _kernel_id_regex, KernelHandler),
            (r"/kernels/%s/%s" % (_kernel_id_regex, _kernel_action_regex), KernelActionHandler),
            (r"/kernels/%s/iopub" % _kernel_id_regex, IOPubHandler),
            (r"/kernels/%s/shell" % _kernel_id_regex, ShellHandler),
        ]

        # Python < 2.6.5 doesn't accept unicode keys in f(**kwargs), and
        # base_project_url will always be unicode, which will in turn
        # make the patterns unicode, and ultimately result in unicode
        # keys in kwargs to handler._execute(**kwargs) in tornado.
        # This enforces that base_project_url be ascii in that situation.
        # 
        # Note that the URLs these patterns check against are escaped,
        # and thus guaranteed to be ASCII: 'héllo' is really 'h%C3%A9llo'.
        
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path='static',
            cookie_secret='secret',
            cookie_name='ignored',
        )

        super(WebApp, self).__init__(handlers, **settings)

        self.kernel_manager = kernel_manager
        self.kernel_id = kernel_id
        self.log = log
        # unused stuff, required by our handlers
        self.password = ''
        self.read_only = False
        self.ipython_app = DummyIPythonApp()
        # self.config = self.ipython_app.config


#-----------------------------------------------------------------------------
# start the app
#-----------------------------------------------------------------------------

def main():
    kernel_manager = MultiKernelManager()
    # give the KernelManager attributes it shouldn't need,
    # but IPython's handlers require:
    kernel_manager.max_msg_size = 100*1024*1024
    kernel_manager.time_to_dead = 1000
    kernel_manager.first_beat = 1000
    
    # we are only using one kernel:
    kernel_id = '1'
    kernel_manager.start_kernel(kernel_id=kernel_id)
    
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger()
    app = WebApp(kernel_manager, kernel_id, log)
    server = httpserver.HTTPServer(app)
    server.listen(8000, '127.0.0.1')
    log.info("Serving at http://127.0.0.1:8000")
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        log.info("Interrupted...")
    finally:
        kernel_manager.shutdown_all()


if __name__ == '__main__':
    main()

