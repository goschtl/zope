import ClientForm
import os.path
import re
import simplejson
import socket
import telnetlib
import time
import urlparse
import zc.testbrowser.browser
import zc.testbrowser.interfaces
import zope.interface

PROMPT = re.compile('repl\d?> ')

class BrowserStateError(RuntimeError):
    pass

class Browser(zc.testbrowser.browser.SetattrErrorsMixin):
    zope.interface.implements(zc.testbrowser.interfaces.IBrowser)

    base = None
    raiseHttpErrors = True
    _counter = 0
    timeout = 5 # XXX debug only, change back to 60

    def __init__(self, url=None, host='localhost', port=4242):
        self.timer = zc.testbrowser.browser.PystoneTimer()
        self.init_repl(host, port)
        self._enable_setattr_errors = True

        if url is not None:
            self.open(url)

    def init_repl(self, host, port):
        dir = os.path.dirname(__file__)
        js_path = os.path.join(dir, 'real.js')
        try:
            self.telnet = telnetlib.Telnet(host, port)
        except socket.error, e:
            raise RuntimeError('Error connecting to Firefox at %s:%s.'
                ' Is MozRepl running?' % (host, port))

        self.telnet.write(open(js_path, 'rt').read())
        self.expect([PROMPT])

    def execute(self, js):
        if not js.strip():
            return
        self.telnet.write("'MARKER'")
        self.telnet.read_until('MARKER')
        self.expect([PROMPT])
        self.telnet.write(js)
        i, match, text = self.expect([PROMPT])
        if '!!!' in text: import pdb;pdb.set_trace() # XXX debug only, remove
        result = text.rsplit('\n', 1)
        if len(result) == 1:
            return None
        else:
            return result[0]

    def executeLines(self, js):
        lines = js.split('\n')
        for line in lines:
            self.execute(line)

    def expect(self, res):
        i, match, text = self.telnet.expect([PROMPT], self.timeout)
        if match is None:
            raise RuntimeError('unexpected result from MozRepl')
        return i, match, text

    def _changed(self):
        self._counter += 1

    @property
    def url(self):
        return self.execute('content.location')

    def waitForPageLoad(self):
        start = time.time()
        while self.execute('tb_page_loaded') == 'false':
            time.sleep(0.001)
            if time.time() - start > self.timeout:
                raise RuntimeError('timed out waiting for page load')

        self.execute('tb_page_loaded = false;')

    def open(self, url, data=None):
        if self.base is not None:
            url = urlparse.urljoin(self.base, url)
        assert data is None
        self.start_timer()
        try:
            self.execute('content.location = ' + simplejson.dumps(url))
            self.waitForPageLoad()
        finally:
            self.stop_timer()
            self._changed()

        # TODO raise non-200 errors

    @property
    def isHtml(self):
        return self.execute('content.document.contentType') == 'text/html'

    @property
    def title(self):
        if not self.isHtml:
            raise BrowserStateError('not viewing HTML')

        result = self.execute('content.document.title')
        if result is '':
            result = None
        return result

    @property
    def contents(self):
        return self.execute('content.document.documentElement.innerHTML')

    @property
    def headers(self):
        raise NotImplementedError

    @apply
    def handleErrors():
        def get(self):
            raise NotImplementedError

        def set(self, value):
            raise NotImplementedError

        return property(get, set)

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()

    @property
    def lastRequestPystones(self):
        return self.timer.elapsedPystones

    @property
    def lastRequestSeconds(self):
        return self.timer.elapsedSeconds

    def reload(self):
        self.start_timer()
        self.execute('content.document.location = content.document.location')
        self.waitForPageLoad()
        self.stop_timer()

    def goBack(self, count=1):
        self.start_timer()
        self.execute('content.back()')
        # Our method of knowing when the page finishes loading doesn't work
        # for "back", so for now just sleep a little, and hope it is enough.
        time.sleep(1)
        self.stop_timer()
        self._changed()

    def addHeader(self, key, value):
        raise NotImplementedError

    def getLink(self, text=None, url=None, id=None, index=0):
        zc.testbrowser.browser.onlyOne((text, url, id), 'text, url, or id')
        js_index = simplejson.dumps(index)
        if text is not None:
            msg = 'text %r' % text
            token = self.execute('tb_get_link_by_text(%s, %s)'
                 % (simplejson.dumps(text), js_index))
        elif url is not None:
            msg = 'url %r' % url
            token = self.execute('tb_get_link_by_url(%s, %s)'
                 % (simplejson.dumps(url), js_index))
        elif id is not None:
            msg = 'id %r' % id
            token = self.execute('tb_get_link_by_id(%s, %s)'
                 % (simplejson.dumps(id), js_index))

        if token == 'false':
            raise ValueError('Link not found: ' + msg)
        if token == 'ambiguity error':
            raise ClientForm.AmbiguityError(msg)

        return Link(token, self)

    def _follow_link(self, token):
        self.execute('tb_follow_link(%s)' % token)

    def getControl(self, label=None, name=None, index=None):
        raise NotImplementedError

    def getForm(self, id=None, name=None, action=None, index=None):
        raise NotImplementedError


class Link(zc.testbrowser.browser.SetattrErrorsMixin):
    zope.interface.implements(zc.testbrowser.interfaces.ILink)

    def __init__(self, token, browser):
        self.token = token
        self.browser = browser
        self._browser_counter = self.browser._counter
        self._enable_setattr_errors = True

    def click(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        self.browser.start_timer()
        self.browser._follow_link(self.token)
        self.browser.stop_timer()
        self.browser._changed()

    @property
    def url(self):
        return self.browser.execute('tb_tokens[%s].href' % self.token)

    @property
    def text(self):
        return self.browser.execute('tb_get_link_text(%s)' % self.token)

    def __repr__(self):
        return "<%s text=%r url=%r>" % (
            self.__class__.__name__, self.text, self.url)
