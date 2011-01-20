zc.customdoctests -- customized doctest implementations
*******************************************************

doctest (and recently manuel) provide hooks for using custo doctest
parsers. This enables writing JavaScript doctests, as in::

    js> function double (x) { return x*2; }
    js> double(2)
    4

And with manuel, it facilitates doctests that mix multiple languages,
such as Python, JavaScript, and sh.

Changes
*******

0.1.0 (yyyy-mm-dd)
==================

Initial release
