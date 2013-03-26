# coding: utf-8
"""A simple webapp backed by an IPython Kernel

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
import os

from tornado import web

# IPython
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

class BesselHandler(web.RequestHandler):
    def get(self):
        return self.render('besselfunctions.html')

class DummyIPythonApp(object):
    """It's dumb that we need this"""
    websocket_host = 'localhost:8000'

class BesselFunctionWebApp(web.Application):

    def __init__(self, kernel_manager, kernel_id, log):
        handlers = [
            (r"/", BesselHandler),
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

        super(BesselFunctionWebApp, self).__init__(handlers, **settings)

        self.kernel_manager = kernel_manager
        self.kernel_id = kernel_id
        self.log = log
        # unused stuff, required by our handlers
        self.password = ''
        self.read_only = False
        self.ipython_app = DummyIPythonApp()
        # self.config = self.ipython_app.config

