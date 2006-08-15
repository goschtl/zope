"""Microsoft Rich Text Format support library.

See rtflib.txt for documentation and tests.

"""
__docformat__ = "reStructuredText"

CHUNK_SIZE = 1024 * 16


class RtfContentHandler(object):

    # If _levels is not None, _levels[-1] is the "uc" value, used in
    # conjunction with unicode characters.
    _levels = 0

    def startGroup(self):
        self._levels += 1

    def endGroup(self):
        self._levels -= 1
        if self._levels < 0:
            raise ValueError("too many groups closed")

    def command(self, cmd, arg):
        pass

    def characters(self, text):
        pass

    def startDocument(self):
        pass

    def endDocument(self):
        if self._levels:
            raise ValueError("too few groups closed")


class RtfReader(object):

    _buffer = ""
    _skip_bytes = 0
    _started = False

    def __init__(self, handler=None):
        self._stack = RtfState()
        if handler is None:
            handler = RtfContentHandler()
        self.handler = handler

    def parseStream(self, stream):
        data = stream.read(CHUNK_SIZE)
        while data:
            self.feed(data)
            data = stream.read(CHUNK_SIZE)
        self.close()

    def parseString(self, data):
        self.feed(data)
        self.close()

    def feed(self, data):
        if not self._started:
            self._started = True
            self.handler.startDocument()
        self._buffer += data
        consumed = self.scan(self._buffer)
        if consumed:
            self._buffer = self._buffer[consumed:]

    def close(self):
        consumed = self.scan(self._buffer, end=True)
        if consumed:
            self._buffer = self._buffer[consumed:]
        if self._buffer:
            err = ValueError("data not consumed")
            err.data = self._buffer
            raise err
        if self._skip_bytes:
            raise ValueError("too little data")
        self._buffer = None
        self.handler.endDocument()

    def scan(self, data, end=False):
        if len(data) < self._skip_bytes:
            length = len(data)
            self._skip_bytes -= length
            return length
        i = self._skip_bytes
        self._skip_bytes = 0
        while len(data) > i:
            nc = data[i:i+1]
            if nc == "{":
                i += 1
                self.handler.startGroup()
                self._stack = RtfState(self._stack)
                continue
            if nc == "}":
                i += 1
                self.handler.endGroup()
                self._stack = self._stack.prev
                continue
            if nc == "\\":
                m = _command_rx.match(data, i)
                if m:
                    text, cmd, arg, space = m.group(0, 1, 2, 3)
                    have_token = space or end
                    if not have_token:
                        # we have a token if there's more after this
                        have_token = (i + len(text)) < len(data)
                    if have_token:
                        i += len(text)
                        if arg:
                            arg = int(arg, 10)
                        if cmd == "uc":
                            self._stack.uc = arg
                            self.handler.command(cmd, arg)
                        elif cmd == "ansicpg":
                            if arg is None:
                                raise ValueError(
                                    r"\ansicpg must have an argument")
                            self._stack.cp = "cp%s" % arg
                            self.handler.command(cmd, arg)
                        elif cmd == "u":
                            # unicode character; don't report as a command,
                            # but decode and report as text; doing this here
                            # is needed to deal with the "uc" values properly.
                            if arg < 0:
                                arg += 65536
                            self.handler.characters(unichr(arg))
                            uc = self._stack.uc
                            skipped = data[i:i+uc]
                            i += uc
                            self._skip_bytes = uc - len(skipped)
                        else:
                            if cmd in self._encoding_map:
                                self._stack.cp = self._encoding_map[cmd]
                            self.handler.command(cmd, arg)
                    else:
                        return i
                    continue
                # some sort of escape?
                nc2 = data[i+1:i+2]
                if nc2 == "'":
                    # hex escape:
                    code = data[i+2:i+4]
                    if len(code) < 2:
                        if end:
                            raise ValueError(
                                "incomplete hex escape: %r" % code)
                        return i
                    if not self._stack.cp:
                        raise ValueError("cannot interpret hex escape"
                                         " without code page setting")
                    ch = unicode(chr(int(code, 16)), self._stack.cp)
                    i += 4
                    self.handler.characters(ch)
                elif nc2 == "~":
                    i += 2
                    self.nonBreakingSpace()
                elif nc2 == "_":
                    i += 2
                    self.nonBreakingHyphen()
                elif nc2 == "-":
                    i += 2
                    self.hyphenationPoint()
                elif nc2 in "{}":
                    i += 2
                    self.handler.characters(unicode(nc2, "ascii"))
                elif nc2 == "*":
                    i += 2
                    self.handler.command(nc2, None)
                elif nc2 == "":
                    if end:
                        raise ValueError(r"incomplete token: '\'")
                    return i
                else:
                    # unrecognized "\" sequence
                    i += 2
                continue
            if nc == "\t":
                i += 1
                self.handler.command("tab", None)
                continue
            # something other than {, }, or \
            # (plaintext)
            m = _interesting_rx.search(data, i)
            if m:
                pos = m.start()
                text = data[i:pos]
                i = pos
            else:
                text = data[i:]
                i = len(data)
            text = text.replace("\r", "").replace("\n", "")
            if text:
                self.handler.characters(unicode(text, "ascii"))
        return i

    # If one of the commands listed here is found, the current
    # contenxt is switched use that encoding:
    _encoding_map = {
        # cmd:  encoding
        "ansi": "cp1252",
        "mac":  "mac_roman",
        "pc":   "cp437",
        "pca":  "cp850",
        }

    # These can be replaced by methods that generate the proper
    # Unicode characters is desired; these should be sufficient for
    # text extraction:

    def nonBreakingHyphen(self):
        self.handler.characters(u"-")

    def nonBreakingSpace(self):
        self.handler.characters(u" ")

    def hyphenationPoint(self):
        pass


class RtfState(object):

    __slots__ = "cp", "uc", "prev"

    def __init__(self, prev=None):
        if prev is None:
            self.uc = 1
            self.cp = None
        else:
            self.uc = prev.uc
            self.cp = prev.cp
        self.prev = prev


# Commands are supposed to be lowercase, but the specification warns
# that some older versions of Microsoft Word used some commands that
# included uppercase letters, and that these should continue to be
# accepted.
import re
_command_rx = re.compile(r"\\([a-zA-Z]+)(-?\d+)?( )?")
_interesting_rx = re.compile(r"[\\{}]")
del re
