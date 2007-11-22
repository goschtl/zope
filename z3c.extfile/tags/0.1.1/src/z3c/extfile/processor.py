import time

def parse_header(s):
    l = [e.strip() for e in s.split(';')]
    result_value = l.pop(0).lower()
    result_d = {}
    for e in l:
        try:
            key, value = e.split('=', 1)
        except ValueError:
            continue
        key = key.strip().lower()
        value = value.strip()
        if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        result_d[key] = value
    return result_value, result_d

class Processor:

    def __init__(self, hd):
        self.hd = hd
        self._incoming = []
        # we use a state pattern where the handle method gets
        # replaced by the current handle method for this state.
        self.handle = self.handle_first_boundary

    def pushInput(self, fp, out):
        while True:
            s = fp.read(1024*128)
            if not s:
                return
            lines = s.splitlines(True)
            for line in lines:
                self.pushInputLine(line, out)

    def pushInputLine(self, data, out):
        # collect data
        self._incoming.append(data)
        # if we're not at the end of the line, input was broken
        # somewhere. We return to collect more first.
        if data[-1] != '\n':
            return
        # now use the line in whatever handle method is current
        if len(self._incoming) == 1:
            line = data
        else:
            line = ''.join(self._incoming)
        self._incoming = []

        self.handle(line, out)

    def handle_first_boundary(self, line, out):
        self._boundary = line
        self._last_boundary = self._boundary.rstrip() + '--\r\n'
        self.init_headers()
        self.handle = self.handle_headers
        out.write(line)
        
    def init_headers(self):
        self._disposition = None
        self._disposition_options = {}
        self._content_type = 'text/plain'
        self._content_type_options = {}

    def handle_headers(self, line, out):
        if line in ['\n', '\r\n']:
            out.write(line)
            self.init_data(out)
            return
        key, value = line.split(':', 1)
        key = key.lower()
        if key == "content-disposition":
            self._disposition, self._disposition_options = parse_header(
                value)
        elif key == "content-type":
            self._content_type, self._content_type_options = parse_header(
                value)
            line = line.replace(self._content_type,
                                'application/x-z3c.extfile-info')
        out.write(line)

    def init_data(self, out):
        self._dt_start = time.time()
        filename = self._disposition_options.get('filename')
        # if filename is empty, assume no file is submitted and submit
        # empty file -- don't handle it
        if filename is None or not filename:
            self.handle = self.handle_data
            return
        self._f = self.hd.new()
        self._previous_line = None
        self.handle = self.handle_file_data
        
    def handle_data(self, line, out):
        out.write(line)
        if line == self._boundary:
            self.init_headers()
            self.handle = self.handle_headers
        elif line == self._last_boundary:
            # we should be done
            self.handle = None # shouldn't be called again

    def handle_file_data(self, line, out):
        def _end():
            # write last line, but without \r\n
            self._f.write(self._previous_line[:-2])
            digest = self._f.commit()
            out.write('z3c.extfile.digest:%s' % digest)
            out.write('\r\n')
            out.write(line)
            self._f = None
            self._dt_start = time.time()

        if line == self._boundary:
            _end()
            self.handle = self.handle_headers
        elif line == self._last_boundary:
            _end()
            self._f = None
            self.handle = None # shouldn't be called again
        else:
            if self._previous_line is not None:
                self._f.write(self._previous_line)
            self._previous_line = line
