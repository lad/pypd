pypd
====

Classes and utilities for parsing and manipulating [Pure Data][] patch files. Pure Data (aka *Pd*) is a real-time graphical programming environment for audio
and video.

The original intent of this project is to fill the gap in managing dependencies between Pd patch files. Pd patches may contain references to other patch files (*abstractions* in Pd terminology) and these in turn may references further patch files. However, Pd lacks any way of viewing or managing these dependencies.

The main goal of this project is to make it easier to view and manage these dependencies. Pd is supported in *vanilla* and *extended* forms. Without any tools it is difficult to know if a patch is compatible with pd-vanilla or requires pd-extended. It's easy to inadvertently refer to a local patch file and cause the patch to fail in other installations.

In addition to managing dependencies, having parsed the patch files, a number of useful utilities may be written to manipulate objects within patch files.

NOTE
====

This is a work-in-progress rewrite of the initial version that you can find in the [pypd.archive][] repository.


[Pure Data]: http://puredata.info
[pypd.archive]: https://github.com/lad/PyPd.Archive

