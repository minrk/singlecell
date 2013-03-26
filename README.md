# Simple webapps backed by an IPython Kernel

There's some cleanup to be done on the IPython side,
but this shows two simple apps backed by an IPython Kernel.

Start the app with

    python singlecell.py

The first is a single IPython code cell - this is the most complicated,
with the most dependencies,
because the CodeCell object is actually where most of the IPython Notebook's complexity lies
- it brings in CodeMirror, completion, the tooltip, and other things, all of which are not optional.
Some of this needs to be cleaned up.

The other demo is a plain webapp - no IPython input cell or anything,
backed by a kernel, where moving some sliders result in recomputation of plot data,
which is sent to the frontend and plotted with [flot](https://code.google.com/p/flot/).
