A BTree-based persistent dict-like object that can be used as a base class.

This is a bit of a heavyweight solution, as every zc.dict.Dict is at
least 3 persistent objects.  Keep this in mind if you intend to create
lots and lots of these.
