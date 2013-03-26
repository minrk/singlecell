# coding: utf-8
"""Serve one of two demo webapps, backed by a single IPython Kernel

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
import sys

# Install the pyzmq ioloop. This has to be done before anything else from
# tornado is imported.
from zmq.eventloop import ioloop
ioloop.install()

from tornado import httpserver

# IPython
from IPython.kernel.multikernelmanager import MultiKernelManager

from besselfunctions import BesselFunctionWebApp
from singlecell import SingleCellWebApp

#-----------------------------------------------------------------------------
# start the app
#-----------------------------------------------------------------------------

def main(app_class):
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
    app = app_class(kernel_manager, kernel_id, log)
    server = httpserver.HTTPServer(app)
    server.listen(8000, '127.0.0.1')
    log.info("Serving %s at http://127.0.0.1:8000" % app_class.__name__)
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        log.info("Interrupted...")
    finally:
        kernel_manager.shutdown_all()
    
    
    

if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'bessel':
        app_class = BesselFunctionWebApp
    else:
        app_class = SingleCellWebApp
    main(app_class)

