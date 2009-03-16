BTree-based persistent dict-like objects (regular dict and ordered) that can be
used as base classes.

This is a bit of a heavyweight solution, as every zc.dict.Dict (and
zc.dict.OrderedDict) is at least 3 persistent objects.  Keep this in
mind if you intend to create lots and lots of these.

To build, run ``python bootstrap/bootstrap.py`` and then ``bin/buildout``
from this directory.  A clean, non-system Python is strongly recommended.
