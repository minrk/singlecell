//----------------------------------------------------------------------------
//  Copyright (C) 2013  The IPython Development Team
//
//  Distributed under the terms of the BSD License.  The full license is in
//  the file COPYING, distributed as part of this software.
//----------------------------------------------------------------------------

//============================================================================
// On document ready
//============================================================================

init_namespace = function(kernel) {
    var code = "import json\n" +
    "from IPython.core.display import JSON, display\n" +
    "from scipy.special import jn\n" +
    "from numpy import linspace\n" +

    "def update_plot(n, xmax=10, npoints=200):\n" +
    "    x = linspace(0, xmax, npoints)\n" +
    "    lines = []\n" +
    "    for i in range(1,n+1):\n" +
    "        lines.append(zip(x,jn(x,i)))\n" +
    "    display(JSON(json.dumps(lines)))";
    kernel.execute(code, {});
}

update_plot = function(msg_type, content){
    // callback for updating the plot with the output of the request
    if (msg_type !== 'display_data')
        return;
    var lines = content['data']['application/json'];
    if (lines != undefined){
        lines = JSON.parse(lines);
        $.plot($("#theplot"), lines);
    } else {
        console.log("no lines?!");
        console.log(data);
    }
};

do_request_update = function(kernel){
    // execute update on the kernel
    var n = $('div#n_slider').slider("value");
    $('span#n_label').text("n = " + n);
    
    var xmax = $('div#xmax_slider').slider("value");
    $('span#xmax_label').text("xmax = " + xmax);
    
    var npoints = $('div#npoints_slider').slider("value");
    $('span#npoints_label').text("npoints = " + npoints);
    
    var args = n + ", xmax=" + xmax + ", npoints=" + npoints;
    kernel.execute("update_plot(" + args + ")", {'output': update_plot});
};

$(document).ready(function () {

    $([IPython.events]).on('status_started.Kernel', function(evt, data) {
        setTimeout(function() {
            init_namespace(data.kernel);
            do_request_update(data.kernel);
        }, 500);
    });
    
    // setup our sliders


    var kernel = new IPython.Kernel('/kernels');
    
    request_update = function() {
        do_request_update(kernel);
    }

    $('div#n_slider').slider({
        min : 1,
        max : 20,
        value : 4,
        slide : request_update,
        change: request_update
    });
    $('div#xmax_slider').slider({
        min : 1,
        max : 32,
        step : 0.2,
        value : 10,
        slide : request_update,
        change: request_update
    });
    $('div#npoints_slider').slider({
        min : 2,
        max : 128,
        step : 1,
        value : 100,
        slide : request_update,
        change: request_update
    });
    
    var ws_url = 'ws' + document.location.origin.substring(4) + '/';
    setTimeout(function() {
        kernel._kernel_started({kernel_id: '1', ws_url: ws_url});
    }, 500);
    
    $("a#restart").click(function() {
        kernel.restart();
    })
    $("a#interrupt").click(function() {
        kernel.interrupt();
    })
});

