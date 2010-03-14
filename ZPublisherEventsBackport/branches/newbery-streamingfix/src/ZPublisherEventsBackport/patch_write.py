import tempfile
import thread

from zope.event import notify
from pubevents import PubSuccess
from ZServer.Producers import file_part_producer


def zserver_write(self, data, request=None):
    """\
    Return data as a stream

    HTML data may be returned using a stream-oriented interface.
    This allows the browser to display partial results while
    computation of a response to proceed.

    The published object should first set any output headers or
    cookies on the response object.

    Note that published objects must not generate any errors
    after beginning stream-oriented output.

    """

    if type(data) != type(''):
        raise TypeError('Value must be a string')

    stdout=self.stdout

    if not self._wrote:
        if request is not None:
            notify(PubSuccess(request))
        l=self.headers.get('content-length', None)
        if l is not None:
            try:
                if type(l) is type(''): l=int(l)
                if l > 128000:
                    self._tempfile=tempfile.TemporaryFile()
                    self._templock=thread.allocate_lock()
            except: pass

        self._streaming=1
        stdout.write(str(self))
        self._wrote=1

    if not data: return

    if self._chunking:
        data = '%x\r\n%s\r\n' % (len(data),data)

    l=len(data)

    t=self._tempfile
    if t is None or l<200:
        stdout.write(data)
    else:
        b=self._tempstart
        e=b+l
        self._templock.acquire()
        try:
            t.seek(b)
            t.write(data)
        finally:
            self._templock.release()
        self._tempstart=e
        stdout.write(file_part_producer(t,self._templock,b,e), l)

def zpublisher_write(self, data, request=None):
    """\
    Return data as a stream

    HTML data may be returned using a stream-oriented interface.
    This allows the browser to display partial results while
    computation of a response to proceed.

    The published object should first set any output headers or
    cookies on the response object.

    Note that published objects must not generate any errors
    after beginning stream-oriented output.

    """
    if not self._wrote:
        if request is not None:
            notify(PubSuccess(request))
        self.outputBody()
        self._wrote = 1
        self.stdout.flush()

    self.stdout.write(data)

