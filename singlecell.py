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

try:
    from tornado.log import app_log
except ImportError:
    logging.basicConfig()
    app_log = logging.getLogger()


# IPython
from IPython.kernel.multikernelmanager import MultiKernelManager

from IPython.frontend.html.notebook.handlers import (
    KernelHandler, KernelActionHandler,
    IOPubHandler, ShellHandler, StdinHandler,
)
from IPython.frontend.html.notebook.notebookapp import (
    _kernel_action_regex,
)

#-----------------------------------------------------------------------------
# The Tornado web application
#-----------------------------------------------------------------------------

_kernel_id_regex = r"(?P<kernel_id>\w+)"

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

    def __init__(self, kernel_manager):
        handlers = [
            (r"/", IndexHandler),
            (r"/singlecell", SingleCellHandler),
            (r"/bessel", BesselHandler),
            (r"/kernels/%s" % _kernel_id_regex, KernelHandler),
            (r"/kernels/%s/%s" % (_kernel_id_regex, _kernel_action_regex), KernelActionHandler),
            (r"/kernels/%s/iopub" % _kernel_id_regex, IOPubHandler),
            (r"/kernels/%s/shell" % _kernel_id_regex, ShellHandler),
            (r"/kernels/%s/stdin" % _kernel_id_regex, StdinHandler),
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
            kernel_manager=kernel_manager,
        )

        super(WebApp, self).__init__(handlers, **settings)


#-----------------------------------------------------------------------------
# start the app
#-----------------------------------------------------------------------------

def main():
    kernel_manager = MultiKernelManager()
    
    # we are only using one kernel:
    kernel_id = '1'
    kernel_manager.start_kernel(kernel_id=kernel_id)
    
    logging.basicConfig(level=logging.INFO)
    app = WebApp(kernel_manager)
    server = httpserver.HTTPServer(app)
    server.listen(8000, '127.0.0.1')
    app_log.info("Serving at http://127.0.0.1:8000")
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        app_log.info("Interrupted...")
    finally:
        kernel_manager.shutdown_all()


if __name__ == '__main__':
    main()

