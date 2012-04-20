import sys

PY3 = sys.version_info[0] >= 3

if PY3: #pragma NO COVER
    import builtins
    def b(s):
        return s.encode("latin-1")
    def u(s):
        return s
    string_types = str,
    text_type = str
    binary_type = bytes
    integer_types = int,
    print_ = getattr(builtins, "print")
else: #pragma NO COVER
    def b(s):
        return s
    def u(s):
        return unicode(s, "unicode_escape")
    string_types = basestring,
    text_type = unicode
    binary_type = str
    integer_types = (int, long)

    def print_(*args, **kwargs):
        """The new-style print function."""
        fp = kwargs.pop("file", sys.stdout)
        if fp is None:
            return
        def write(data):
            if not isinstance(data, basestring):
                data = str(data)
            fp.write(data)
        want_unicode = False
        sep = kwargs.pop("sep", None)
        if sep is not None:
            if isinstance(sep, unicode):
                want_unicode = True
            elif not isinstance(sep, str):
                raise TypeError("sep must be None or a string")
        end = kwargs.pop("end", None)
        if end is not None:
            if isinstance(end, unicode):
                want_unicode = True
            elif not isinstance(end, str):
                raise TypeError("end must be None or a string")
        if kwargs:
            raise TypeError("invalid keyword arguments to print()")
        if not want_unicode:
            for arg in args:
                if isinstance(arg, unicode):
                    want_unicode = True
                    break
        if want_unicode:
            newline = unicode("\n")
            space = unicode(" ")
        else:
            newline = "\n"
            space = " "
        if sep is None:
            sep = space
        if end is None:
            end = newline
        for i, arg in enumerate(args):
            if i:
                write(sep)
            write(arg)
        write(end)
