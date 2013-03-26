//----------------------------------------------------------------------------
//  Copyright (C) 2013  The IPython Development Team
//
//  Distributed under the terms of the BSD License.  The full license is in
//  the file COPYING, distributed as part of this software.
//----------------------------------------------------------------------------

//============================================================================
// On document ready
//============================================================================


$(document).ready(function () {

    // monkey patch CM to be able to syntax highlight cell magics
    // bug reported upstream,
    // see https://github.com/marijnh/CodeMirror2/issues/670
    if(CodeMirror.getMode(1,'text/plain').indent == undefined ){
        console.log('patching CM for undefined indent');
        CodeMirror.modes.null = function() { return {token: function(stream) {stream.skipToEnd();},indent : function(){return 0}}}
        }

    CodeMirror.patchedGetMode = function(config, mode){
            var cmmode = CodeMirror.getMode(config, mode);
            if(cmmode.indent == null)
            {
                console.log('patch mode "' , mode, '" on the fly');
                cmmode.indent = function(){return 0};
            }
            return cmmode;
        }
    // end monkey patching CodeMirror
    IPython.tooltip = new IPython.Tooltip()

    var kernel = new IPython.Kernel('/kernels');
    var ws_url = 'ws' + document.location.origin.substring(4);
    kernel._kernel_started({kernel_id: '1', ws_url: ws_url});
    var thecell = new IPython.CodeCell(kernel);
    $("div#thecell").append(thecell.element);
    
    $(document).keydown(function (event) {
        var key = IPython.utils.keycodes;
        
        if (event.which === key.ESC) {
            // Intercept escape at highest level to avoid closing
            // websocket connection with firefox
            event.preventDefault();
        } else if (event.which === key.SHIFT) {
            // ignore shift keydown
            return true;
        }
        if (event.which === key.ENTER && event.shiftKey) {
            thecell.execute();
            return false;
        }
    });
    $("a#restart").click(function() {
        kernel.restart();
    })
    $("a#interrupt").click(function() {
        kernel.interrupt();
    })
});

