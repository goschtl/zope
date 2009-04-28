##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import logging
import os
import os.path
import re
import simplejson
import socket
import telnetlib
import tempfile
import signal
import time
import urlparse

import zc.testbrowser.browser
import zc.testbrowser.interfaces
from zc.testbrowser import utils

import zope.interface

import mozrunner

PROMPT = re.compile('repl\d?> ')
CONTINUATION_PROMPT = re.compile('\\.\\.\\.\\.\d?> ')

class MozReplProfile(mozrunner.FirefoxProfile):
    """A mozrepl enabled firefox profile"""

    def set_preferences(self, preferences):
        """Adds preferences dict to profile preferences"""
        pref_lines = ['user_pref(%s, %s);' %
                      (simplejson.dumps(k),
                       simplejson.dumps(v).replace('\/', '/' )) for k, v in
                      preferences.items()]
        prefs_file = os.path.join(self.profile, 'user.js')
        gen_prefs_file = os.path.join(self.profile, 'prefs.js')
        for fp in prefs_file, gen_prefs_file:
            f = open(fp, 'a+')
            f.write('\n#MozRunner Prefs Start\n')
            for line in pref_lines:
                f.write(line+'\n')
            f.write('#MozRunner Prefs End\n')
            f.flush()
            f.close()

    def __init__(self,
                 default_profile=None,
                 profile=None,
                 create_new=True,
                 plugins=[],
                 preferences={},
                 port=4242,
                 *args, **kwargs):
        """See mozrunner code for documentation.
        port: port where mozrepl should listen on"""
        plugins.append(
            os.path.join(os.path.dirname(__file__), 'firefox', 'mozrepl.xpi')
        )
        # update preferences to activate mozrepl on firefox startup
        # depending the mozrepl version, keys can changed!
        self.preferences.update(
            {'extensions.mozlab.mozrepl.autoStart': True,
             'extensions.mozlab.mozrepl.loopbackOnly': False,
             'extensions.mozlab.mozrepl.port': port,
             'extensions.mozlab.mozrepl.autoStart': True,
             'extensions.mozrepl.autoStart': True,
             'extensions.mozrepl.loopbackOnly': False,
             'extensions.mozrepl.port': port,
             'extensions.mozrepl.autoStart': True,
            }
        )
        mozrunner.FirefoxProfile.__init__(self,
                                          default_profile=default_profile,
                                          profile=profile,
                                          create_new=create_new,
                                          plugins=plugins,
                                          preferences=preferences,
                                          *args, **kwargs)

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
    """A firefox based browser controller.
    It supports firefox launching through mozrunner if the host is localhost
    """

    zope.interface.implements(zc.testbrowser.interfaces.IBrowser,
        zc.testbrowser.interfaces.IWait)

    base = None
    raiseHttpErrors = True
    _counter = 0
    timeout = 60

    def __init__(self,
                 url=None,
                 host = None,
                 port=None,
                 firefox_binary = None,
                 profile_klass = None,
                 config=None,
                 preferences = None,
                 *args, **kwargs):

        self._enable_setattr_errors = False
        self.log = logging.getLogger(__name__)
        self.js = JSProxy(self.execute)
        self.config = utils.get_ztb_config(config)
        self.host = host
        self.port = port
        if not profile_klass:
            profile_klass = MozReplProfile
        if not preferences:
            preferences = {}
        # those are path location only !
        self.MOZILLA_BINARY = firefox_binary
        if not self.host:
            self.host = self.config.get('firefox-host', 'localhost')
        if not port:
            self.port = self.config.get('firefox-port',  4242)
        if not self.MOZILLA_BINARY:
            self.MOZILLA_BINARY = self.config.get('firefox',
                os.environ.get('FIREFOX', 'firefox')
            ).strip()
        # for local addresses, just load directly the file, its really faster
        hosts = socket.gethostbyaddr(socket.getaddrinfo(self.host, 0)[0][4][0])[1]

        self.is_local = 'localhost' in hosts
        # if we are local, we are just enought smarts to handle firefox
        # starts/stops
        self.firefox_profile, self.firefox = None, None
        if self.is_local:
            self.firefox_profile = profile_klass(port=self.port, preferences=preferences)
            self.firefox = mozrunner.FirefoxRunner(binary=utils.which(self.MOZILLA_BINARY),
                                                   profile=self.firefox_profile)
        self.firefox_running = False
        # this will be a no-op if we are not attacking a local mozrepl.
        self.start_ff()
        if url is not None:
            self.open(url)

    def init_repl(self, host, port):
        try:
            self._enable_setattr_errors = False
            self.telnet = telnetlib.Telnet(host, port)
            self._enable_setattr_errors = True
        except socket.error, e:
            raise RuntimeError('Error connecting to Firefox at %s:%s.'
                ' Is MozRepl running?' % (host, port))
        self.load_realjs()

    def load_realjs(self):
        dir = os.path.dirname(__file__)
        js_path = os.path.join(dir, 'real.js')
        self.load_file(js_path)

    def load_file(self, file_path):
        # for local addresses, just load directly the file, its really faster
        self.assert_repl_initialized()
        hosts = socket.gethostbyaddr(
            socket.getaddrinfo(self.telnet.host, 0)[0][4][0]
        )[1]
        if self.is_local:
            self.telnet.write('repl.load("file://%s")' % file_path)
        else:
            for line in open(file_path, 'r'):
                self.telnet.write(line)
        self.expect([PROMPT, CONTINUATION_PROMPT])

    def execute(self, js):
        self.assert_repl_initialized()
        if not js.strip():
            return
        if not js.endswith('\n'):
            js = js + '\n'
        # wipe the line from previous dusts in the channel
        self.telnet.write("\n;\n")
        #print self.telnet.read_until('MARKER', self.timeout)
        self.expect()
        self.telnet.write(js)
        i, match, text = self.expect()
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

    def assert_repl_initialized(self):
        assert getattr(self, 'telnet', None), 'MozRepl is not initialized'

    def expect(self, expected=None):
        self.assert_repl_initialized()
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


    def update_profile(self, prefs=None):
        if prefs:
            self.firefox.profile.preferences.update(prefs)
        self.firefox_profile.set_preferences(
            self.firefox_profile.preferences
        )

    def wait(self):
        start = time.time()
        while self.execute('tb_page_loaded') == 'false':
            time.sleep(0.001)
            if time.time() - start > self.timeout:
                raise RuntimeError('timed out waiting for page load')

        #ret = self.execute('tb_page_loaded;')
        retrys = 100
        assertion = None
        while retrys and not assertion:
            retrys -= 1
            time.sleep(0.01)
            assertion = self.execute('tb_page_loaded;')
        assert assertion == 'true'

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
        command = 'tb_get_contents()'
        return self.execute(command)

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

    def exec_contentjs(self, cmd):
        d = {'s': self.getPrompt(), 'cmd': cmd}
        try:
            self.home()
            ret = self.execute("this.content.%(cmd)s; " % d)
        except Exception, e:
            raise
        finally:
            self.home()
        return ret

    def quit_mozrepl(self):
        self._enable_setattr_errors = False
        self._prompt = None
        try:
            self.telnet.close()
        except Exception, e:
            pass
        try:
            delattr(self, 'telnet')
        except Exception, e:
            pass
        self._enable_setattr_errors = True

    def home(self):
        self.execute("%s.home()" % self.getPrompt())

    def getPrompt(self, force = True):
        self.assert_repl_initialized()
        self.telnet.write("\n;\n")
        if not getattr(self, '_prompt', None) or force:
            a, g, c = self.expect()
            self._enable_setattr_errors = False
            self._prompt = re.sub('> .*', '', g.group())
            self._enable_setattr_errors = True
        return getattr(self, '_prompt', 'repl')

    def exec_in_ff_dir(self, f, *args, **kwargs):
        """Runs the runner in the firefox directory, if any
        If firefox is not runned on a standart location,
        there are chances you ll get dynamic libraries problems.
        Solution is to be chdir'ed prior to the firefox launch"""
        ret, cwd = None, os.getcwd()
        if self.is_local:
            d = os.path.dirname(self.firefox.binary)
            os.chdir(d)
            try:
                ret = f(*args, **kwargs)
                os.chdir(cwd)
            except Exception, e:
                os.chdir(cwd)
                raise
        return ret

    def start_ff(self):
        """Starts firefox, only if firefox isnt running already."""
        if not self.firefox_running:
            self.exec_in_ff_dir(self.firefox.start)
        time.sleep(1)
        retry = 60
        while retry:
            retry -= 1
            time.sleep(1)
            try:
                self.init_repl(self.host, self.port)
                retry = False
            except Exception, e:
                if not retry:
                    raise
        # considere that firefox is running only if both the couple:
        # firefox / MozRepl connexion is achieved.
        self.firefox_running = True

    def stop_ff(self):
        """Stops firefox, only if firefox is running."""
        if self.firefox_running:
            self.exec_in_ff_dir(
                self.firefox.kill,
                signal.SIGKILL
            )
            self.quit_mozrepl()
            self.firefox_running = False

    def restart_ff(self):
        self.stop_ff()
        time.sleep(1)
        self.start_ff()
        time.sleep(1)

    def screenshot(self, path=".", name="screenshot"):
        if not os.path.exists(path):
            os.makedirs(path)
        fpath = os.path.join(path, "%s.png" % name)
        self.execute('tb_take_screen_shot("%s")' % fpath)
        timeout = 12000
        while not os.path.isfile(fpath) or not timeout:
            timeout -= 1
            time.sleep(0.01)
        if not timeout:
            raise 'Timeout while taking shot!'

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
        self.browser.wait()
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
        self.browser.wait()
        self.browser._changed()


class ImageControl(Control):
    zope.interface.implements(zc.testbrowser.interfaces.IImageSubmitControl)

    def click(self, coord=(1,1)):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        self.browser.js.tb_click_token(self.token, *coord)
        self.browser.wait()
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
        self.browser.wait()
        self.browser._changed()

    def getControl(self, label=None, name=None, index=None):
        if self._browser_counter != self.browser._counter:
            raise zc.testbrowser.interfaces.ExpiredError
        return self.browser.getControl(
            label, name, index, self.token)
