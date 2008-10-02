import os.path
import re
import simplejson
import socket
import telnetlib
import tempfile
import time
import urlparse
import zc.testbrowser.browser
import zc.testbrowser.interfaces
import zope.interface

PROMPT = re.compile('repl\d?> ')
CONTINUATION_PROMPT = re.compile('\\.\\.\\.\\.\d?> ')

class BrowserStateError(RuntimeError):
    pass


class AmbiguityError(ValueError):
    pass


def disambiguate(intermediate, msg, index):
    if intermediate:
        if index is None:
            if len(intermediate) > 1:
                raise AmbiguityError(msg)
            else:
                return intermediate[0]
        else:
            try:
                return intermediate[index]
            except KeyError:
                msg = '%s index %d' % (msg, index)
    raise LookupError(msg)


def controlFactory(token, browser, selectionItem=False):
    tagName = browser.execute('tb_tokens[%s].tagName' % token).lower()
    if tagName == 'select':
        return ListControl(token, browser)
    elif tagName == 'option':
        return ItemControl(token, browser)

    inputType = browser.execute('tb_tokens[%s].getAttribute("type")'
                                % token)
    if inputType is not None:
        inputType = inputType.lower()
    if inputType in ('checkbox', 'radio'):
        if selectionItem:
            return ItemControl(token, browser)
        return ListControl(token, browser)
    elif inputType in ('submit', 'button'):
        return SubmitControl(token, browser)
    elif inputType == 'image':
        return ImageControl(token, browser)

    return Control(token, browser)


def any(items):
    return bool(sum([bool(i) for i in items]))


class JSFunctionProxy(object):
    def __init__(self, executor, name):
        self.executor = executor
        self.js_name = name

    def __call__(self, *args):
        js_args = [simplejson.dumps(a) for a in args]
        js = '[%s(%s)].toSource()' % (
            self.js_name, ', '.join(js_args))
        res = self.executor(js)
        # JS has 'null' and 'undefined', python only has 'None'.
        # This hack is sufficient for now.
        if res == '[(void 0)]':
            return None
        return simplejson.loads(res)[0]


class JSProxy(object):
    def __init__(self, executor):
        self.executor = executor

    def __getattr__(self, attr):
        return JSFunctionProxy(self, attr)

    def __call__(self, js):
        js = js.strip()
        if js:
            return self.executor(js)


class Browser(zc.testbrowser.browser.SetattrErrorsMixin):

    zope.interface.implements(zc.testbrowser.interfaces.IBrowser,
        zc.testbrowser.interfaces.IWait)

    base = None
    raiseHttpErrors = True
    _counter = 0
    timeout = 60

    def __init__(self, url=None, host='localhost', port=4242):
        self.js = JSProxy(self.execute)
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

        self.load_file(js_path)

    def load_file(self, file_path):
        for line in open(file_path, 'r'):
            self.telnet.write(line)
            self.expect([PROMPT, CONTINUATION_PROMPT])

    def execute(self, js):
        if not js.strip():
            return
        if not js.endswith('\n'):
            js = js + '\n'
        self.telnet.write("'MARKER'\n")
        self.telnet.read_until('MARKER', self.timeout)
        self.expect()
        self.telnet.write(js)
        i, match, text = self.expect()
        #if '!!!' in text: import pdb;pdb.set_trace() # XXX debug only, remove
        if '!!!' in text: raise Exception('FAILED: ' + text + ' in ' + js)
        result = text.rsplit('\n', 1)
        if len(result) == 1:
            return None
        if result[0].startswith('"') and result[0].endswith('"'):
            return result[0][1:-1]
        return result[0]

    def executeLines(self, js):
        lines = js.split('\n')
        for line in lines:
            self.execute(line)

    def getAttribute(self, token, attr_name):
        return self.getAttributes([token], attr_name)[0]

    def getAttributes(self, tokens, attr_name):
        return self.js.tb_extract_token_attrs(tokens, attr_name)

    def expect(self, expected=None):
        if expected is None:
            expected = [PROMPT]
        i, match, text = self.telnet.expect(expected, self.timeout)
        if match is None:
            raise RuntimeError('unexpected result from MozRepl')
        return i, match, text

    def _changed(self):
        self._counter += 1

    @property
    def url(self):
        url = self.execute('content.location')
        # url is something like this (without the line breaks):
        # 'http://localhost:26118/index.html \xe2\x80\x94 {
        #       href: "http://localhost:26118/index.html",
        #       host: "localhost:26118",
        #       hostname: "localhost",
        #       port: "26118"}'
        # But we only need the URL part
        token = ' \xe2\x80\x94 {'
        if token in url:
            url = url.split(token)[0]
        return url

    def wait(self):
        start = time.time()
        while self.execute('tb_page_loaded') == 'false':
            time.sleep(0.001)
            if time.time() - start > self.timeout:
                raise RuntimeError('timed out waiting for page load')

        assert self.execute('tb_page_loaded;') == 'true'

        while self.execute('tb_page_loaded;') == 'true':
            self.execute('tb_page_loaded = false;')
            time.sleep(0.001)

        assert self.execute('tb_page_loaded;') == 'false'

    def open(self, url, data=None):
        if self.base is not None:
            url = urlparse.urljoin(self.base, url)
        assert data is None
        try:
            self.execute('content.location = ' + simplejson.dumps(url))
            self.wait()
        finally:
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
        base, sub = self.execute('content.document.contentType').split('/')
        if base == 'text' and 'html' not in sub:
            return self.execute(
                "content.document.getElementsByTagName('pre')[0].innerHTML")
        return self.execute('tb_get_contents()')

    def reload(self):
        self.execute('content.document.location = content.document.location')
        self.wait()

    def goBack(self, count=1):
        self.execute('content.back()')
        # Our method of knowing when the page finishes loading doesn't work
        # for "back", so for now just sleep a little, and hope it is enough.
        time.sleep(1)
        self._changed()

    def getLink(self, text=None, url=None, id=None, index=0):
        zc.testbrowser.browser.onlyOne((text, url, id), 'text, url, or id')
        js_index = simplejson.dumps(index)
        if text is not None:
            msg = 'text %r' % text
            token = self.js.tb_get_link_by_text(text, index)
        elif url is not None:
            msg = 'url %r' % url
            token = self.js.tb_get_link_by_url(url, index)
        elif id is not None:
            msg = 'id %r' % id
            token = self.js.tb_get_link_by_id(id, index)

        if token is False:
            raise zc.testbrowser.interfaces.LinkNotFoundError
        elif token == 'ambiguity error':
            raise AmbiguityError(msg)

        return Link(token, self)

    def getControlToken(self, label=None, name=None, index=None,
                        context_token=None, xpath=None):
        js_index = simplejson.dumps(index)
        token = None
        if label is not None:
            msg = 'label %r' % label
            token = self.js.tb_get_control_by_label(
                label, index, context_token, xpath)
        elif name is not None:
            msg = 'name %r' % name
            token = self.js.tb_get_control_by_name(
                name, index, context_token, xpath)
        else:
            raise NotImplementedError

        if token is False:
            raise LookupError(msg)
        elif token == 'ambiguity error':
            raise AmbiguityError(msg)
        return token

    def getControl(self, label=None, name=None, index=None,
                   context_token=None, xpath=None):
        zc.testbrowser.browser.onlyOne([label, name], '"label" and "name"')
        token = self.getControlToken(label, name, index, context_token, xpath)

        selectionItem = False
        if label is not None:
            inputType = self.execute(
                'tb_tokens[%s].getAttribute("type")' % token)
            if inputType and inputType.lower() in ('radio', 'checkbox'):
                selectionItem = True

        return controlFactory(token, self, selectionItem)

    def getForm(self, id=None, name=None, action=None, index=None):

        xpath = '//form'
        if id is not None:
            xpath += '[@id=%s]' % repr(id)
        if name is not None:
            xpath += '[@name=%s]' % repr(name)

        matching_tokens = self.js.tb_xpath_tokens(xpath)

        if index is None and not any([id, name, action]):
            if len(matching_tokens) == 1:
                index = 0
            else:
                raise ValueError(
                    'if no other arguments are given, index is required.')

        if action is not None:
            form_actions = self.getAttributes(matching_tokens, 'action')
            matching_tokens = [tok for tok, form_act in zip(matching_tokens,
                                                            form_actions)
                               if re.search(action, form_act)]

        form_token = disambiguate(matching_tokens, '', index)

        return Form(self, form_token)


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
        self.browser.js.tb_click_token(self.token)
        self.browser._changed()

    @property
    def url(self):
        return self.browser.execute('tb_tokens[%s].href' % self.token)

    @property
    def text(self):
        return str(self.browser.js.tb_get_link_text(self.token))

    def __repr__(self):
        return "<%s text=%r url=%r>" % (
            self.__class__.__name__, self.text, self.url)


class Control(zc.testbrowser.browser.SetattrErrorsMixin):
    """A control of a form."""
    zope.interface.implements(zc.testbrowser.interfaces.IControl)

    _enable_setattr_errors = False

    def __init__(self, token, browser):
        self.token = token
        self.browser = browser
        self._browser_counter = self.browser._counter
        self._file = None

        # disable addition of further attributes
        self._enable_setattr_errors = True

    @property
    def disabled(self):
        return self.browser.execute(
            'tb_tokens[%s].hasAttribute("disabled")' % self.token) == 'true'

    @property
    def type(self):
        if self.browser.execute('tb_tokens[%s].tagName'
                                % self.token).lower() == 'textarea':
            return 'textarea'

        return self.browser.execute(
            'tb_tokens[%s].getAttribute("type")' % self.token)

    @property
    def name(self):
        return self.browser.execute(
            'tb_tokens[%s].getAttribute("name")' % self.token)

    @property
    def multiple(self):
        if self.type == 'file':
            return False
        return self.browser.execute(
            'tb_tokens[%s].hasAttribute("multiple")' % self.token) == 'true'

    @apply
    def value():

        def fget(self):
            if self.type == 'textarea':
                return self.browser.execute('tb_tokens[%s].value'
                                            % self.token)
            return self.browser.execute(
                'tb_tokens[%s].getAttribute("value")' % self.token)

        def fset(self, value):
            if self._browser_counter != self.browser._counter:
                raise zc.testbrowser.interfaces.ExpiredError

            if self.type == 'file':
                self.add_file(value, content_type=self.content_type,
                              filename=self.filename)
            elif self.type == 'textarea':
                self.browser.execute('tb_tokens[%s].value = %r'
                                     % (self.token, value))
            elif self.type == 'checkbox' and len(self.mech_control.items) == 1:
                self.mech_control.items[0].selected = bool(value)
            else:
                self.browser.execute(
                    'tb_tokens[%s].setAttribute("value", %s)' %(
                    self.token, simplejson.dumps(value)))
        return property(fget, fset)

    def add_file(self, file, content_type, filename):
        if not self.type == 'file':
            raise TypeError("Can't call add_file on %s controls"
                            % self.type)
        if isinstance(file, str):
            file = StringIO(file)
        # Instead of honoring the filename, we are storing the data in a
        # temporary file and reference it:
        fn = os.path.join(tempfile.mkdtemp(), os.path.split(filename)[1])
        dataFile = open(fn, 'w')
        dataFile.write(file.read())
        dataFile.close()
        file.seek(0)
        # Due to a security feature for user-generated Javascript code,
        # browsers do not allow the file upload field's value attribute to be
        # set. But, if we execute the Javascript directly via MozRepl, then
        # this security restriction does not exist.
        id = self.browser.execute('tb_tokens[%s].id' % self.token)
        self.browser.execute(
            'content.document.getElementById("%s").value = %s' % (
            id, simplejson.dumps(fn)))
        # HTML only supports ever setting one file for one input control
        self._file = (file, content_type, filename)

    @property
    def filename(self):
        return self._file[2]

    @property
    def content_type(self):
        return self._file[1]

    def clear(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        self.mech_control.clear()

    def __repr__(self):
        return "<%s name=%r type=%r>" % (
            self.__class__.__name__, self.name, self.type)


class ListControl(Control):
    zope.interface.implements(zc.testbrowser.interfaces.IListControl)

    @property
    def type(self):
        tagName = self.browser.execute(
            'tb_tokens[%s].tagName' % self.token).lower()
        if tagName == 'input':
            return super(ListControl, self).type
        return tagName

    @property
    def multiple(self):
        return self.browser.js.tb_is_listcontrol_multiple(self.token)

    @apply
    def displayValue():
        # not implemented for anything other than select;
        # would be nice if ClientForm implemented for checkbox and radio.
        # attribute error for all others.
        def fget(self):
            return [str(option) for option in
                    self.browser.js.tb_get_listcontrol_displayValue(self.token)]

        def fset(self, value):
            if self._browser_counter != self.browser._counter:
                raise zc.testbrowser.interfaces.ExpiredError
            self.browser.js.tb_set_listcontrol_displayValue(self.token, value)
        return property(fget, fset)

    @property
    def acts_as_single(self):
        return self.browser.js.tb_act_as_single(self.token)

    @apply
    def value():
        def fget(self):
            values = self.browser.js.tb_get_listcontrol_value(self.token)
            if self.acts_as_single:
                return values[0]
            return values

        def fset(self, value):
            if self._browser_counter != self.browser._counter:
                raise zc.testbrowser.interfaces.ExpiredError

            if self.acts_as_single:
                # expects a single value
                self.browser.js.tb_set_checked(self.token, bool(value))
            else:
                # expects a list of control ids
                self.browser.js.tb_set_listcontrol_value(self.token, value)

        return property(fget, fset)

    @property
    def displayOptions(self):
        return [str(option) for option in
                self.browser.js.tb_get_listcontrol_displayOptions(self.token)]

    @property
    def options(self):
        return self.browser.js.tb_get_listcontrol_options(self.token)

    @property
    def controls(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        res = []
        tokens = self.browser.js.tb_get_listcontrol_item_tokens(self.token)
        return [ItemControl(token, self.browser) for token in tokens]

    def getControl(self, label=None, value=None, index=None):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        context_token = self.token
        if self.type in ('checkbox', 'radio'):
            context_token = None
        return self.browser.getControl(
            label, value, index, context_token, ".//input | .//option")


class SubmitControl(Control):
    zope.interface.implements(zc.testbrowser.interfaces.ISubmitControl)

    def click(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        self.browser.js.tb_click_token(self.token)
        self.browser._changed()


class ImageControl(Control):
    zope.interface.implements(zc.testbrowser.interfaces.IImageSubmitControl)

    def click(self, coord=(1,1)):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        self.browser.js.tb_click_token(self.token, *coord)
        self.browser._changed()

    @property
    def value(self):
        return ''

    @property
    def multiple(self):
        return False


class TextAreaControl(Control):
    zope.interface.implements(zc.testbrowser.interfaces.ITextAreaControl)


class ItemControl(zc.testbrowser.browser.SetattrErrorsMixin):
    zope.interface.implements(zc.testbrowser.interfaces.IItemControl)

    def __init__(self, token, browser):
        self.token = token
        self.browser = browser
        self._browser_counter = self.browser._counter
        # disable addition of further attributes
        self._enable_setattr_errors = True

    @property
    def control(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        return controlFactory(self.token, self.browser)

    @property
    def disabled(self):
        return self.browser.execute(
            'tb_tokens[%s].hasAttribute("disabled")' % self.token) == 'true'

    @apply
    def selected():

        def fget(self):
            return self.browser.js.tb_get_checked(self.token)

        def fset(self, value):
            if self._browser_counter != self.browser._counter:
                raise zc.testbrowser.interfaces.ExpiredError
            self.browser.js.tb_set_checked(self.token, bool(value))

        return property(fget, fset)

    @property
    def optionValue(self):
        v = self.browser.execute(
            'tb_tokens[%s].getAttribute("value")' % self.token)

        if not v and self.selected:
            v = 'on'
        return v

    def click(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        if self.disabled:
            raise AttributeError('item is disabled')
        self.selected = not self.selected

    def __repr__(self):
        tagName = self.browser.execute('tb_tokens[%s].tagName' % self.token)
        if tagName.lower() == 'option':
            type = 'select'
            name = self.browser.execute(
                'tb_tokens[%s].parentNode.getAttribute("name")' % self.token)
        else:
            type = self.browser.execute(
                'tb_tokens[%s].getAttribute("type")' % self.token)
            name = self.browser.execute(
                'tb_tokens[%s].getAttribute("name")' % self.token)
        return "<%s name=%r type=%r optionValue=%r selected=%r>" % (
            self.__class__.__name__, name, type, self.optionValue,
            self.selected)


class Form(zc.testbrowser.browser.SetattrErrorsMixin):
    """HTML Form"""
    zope.interface.implements(zc.testbrowser.interfaces.IForm)

    def __init__(self, browser, token):
        self.token = token
        self.browser = browser
        self._browser_counter = self.browser._counter
        self._enable_setattr_errors = True

    @property
    def action(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        action = self.browser.getAttribute(self.token, 'action')
        if action:
            return urlparse.urljoin(self.browser.base, action)
        return self.browser.url

    @property
    def method(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        return self.browser.getAttribute(self.token, 'method').upper()

    @property
    def enctype(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        enc = self.browser.execute('tb_tokens[%s].encoding' % self.token)
        return enc or 'application/x-www-form-urlencoded'

    @property
    def name(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        return self.browser.getAttribute(self.token, 'name')

    @property
    def id(self):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        return self.browser.getAttribute(self.token, 'id')

    def submit(self, label=None, name=None, index=None, coord=(1,1)):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError

        if (label is None and
            name is None):
            self.browser.execute('tb_tokens[%s].submit()' % self.token)
        else:
            button = self.browser.getControlToken(
                label, name, index, self.token)
            self.browser.js.tb_click_token(button, *coord)
        self.browser._changed()

    def getControl(self, label=None, name=None, index=None):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        return self.browser.getControl(
            label, name, index, self.token)
