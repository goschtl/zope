##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Python Page

$Id$
"""
import re
from persistent import Persistent
from zope.app import zapi
from zope.app.container.contained import Contained
from zope.app.interpreter.interfaces import IInterpreter
from zope.interface import Interface, implements
from zope.schema import SourceText, TextLine
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.security.untrustedpython.interpreter import CompiledProgram


class IPythonPage(Interface):
    """Python Page

    The Python Page acts as a simple content type that allows you to execute
    Python in content space. Additionally, if you have a free-standing
    triple-quoted string, it gets converted to a print statement
    automatically.
    """

    source = SourceText(
        title=_("Source"),
        description=_("The source of the Python page."),
        required=True)

    contentType = TextLine(
        title=_("Content Type"),
        description=_("The content type the script outputs."),
        required=True,
        default=u"text/html")

    def __call__(request, **kw):
        """Execute the script.

        The script will insert the 'request' and all '**kw' as global
        variables. Furthermore, the variables 'script' and 'context' (which is
        the container of the script) will be added.
        """


class PythonPage(Contained, Persistent):
    r"""Persistent Python Page - Content Type

    Examples::

      >>> from tests import Root

      >>> pp = PythonPage()
      >>> pp.__parent__ = Root()
      >>> pp.__name__ = 'pp'
      >>> request = None

      Test that can produce the correct filename

      >>> pp._PythonPage__filename()
      u'/pp'

      A simple test that checks that any lone-standing triple-quotes are
      being printed.

      >>> pp.setSource(u"'''<html>...</html>'''")
      >>> pp(request)
      u'<html>...</html>\n'

      Make sure that strings with prefixes work.

      >>> pp.setSource(ur"ur'''test\r'''")
      >>> pp(request)
      u'test\\r\n'

      Make sure that Windows (\r\n) line ends also work.

      >>> pp.setSource(u"if 1 == 1:\r\n\r\n   '''<html>...</html>'''")
      >>> pp(request)
      u'<html>...</html>\n'

      Make sure that unicode strings work as expected.

      >>> pp.setSource(u"u'''\u0442\u0435\u0441\u0442'''")
      >>> pp(request)
      u'\u0442\u0435\u0441\u0442\n'

      Make sure that multi-line strings work.

      >>> pp.setSource(u"u'''test\ntest\ntest'''")
      >>> pp(request)
      u'test\ntest\ntest\n'

      Here you can see a simple Python command...

      >>> pp.setSource(u"print u'<html>...</html>'")
      >>> pp(request)
      u'<html>...</html>\n'

      ... and here a triple quote with some variable replacement.

      >>> pp.setSource(u"'''<html>%s</html>''' %x")
      >>> pp(request, x='test')
      u'<html>test</html>\n'

      Make sure that the context of the page is available.

      >>> pp.setSource(u"'''<html>%s</html>''' %context.__name__")
      >>> pp(request)
      u'<html>root</html>\n'

      Make sure that faulty syntax is interpreted correctly.

      # Note: We cannot just print the error directly, since there is a
      # 'bug' in the Linux version of Python that does not display the filename
      # of the source correctly. So we construct an information string by hand.

      >>> def print_err(err):
      ...     print ('%(msg)s, %(filename)s, line %(lineno)i, offset %(offset)i'
      ...           % err.__dict__)
      ...
      >>> try:
      ...     pp.setSource(u"'''<html>...</html>") #'''"
      ... except SyntaxError, err:
      ...     print_err(err)
      EOF while scanning triple-quoted string, /pp, line 1, offset 19

      >>> try:
      ...     pp.setSource(u"prin 'hello'")
      ... except SyntaxError, err:
      ...     print_err(err)
      invalid syntax, /pp, line 1, offset 12
    """

    implements(IPythonPage)

    def __init__(self, source=u'', contentType=u'text/html'):
        """Initialize the object."""
        super(PythonPage, self).__init__()
        self.source = source
        self.contentType = contentType

    def __filename(self):
        if self.__parent__ is None:
            filename = 'N/A'
        else:
            filename = zapi.getPath(self)
        return filename

    def setSource(self, source):
        r"""Set the source of the page and compile it.

        This method can raise a syntax error, if the source is not valid.
        """
        self.__source = source
        # Make sure the code and the source are synchronized
        if hasattr(self, '_v_compiled'):
            del self._v_compiled

        self.__prepared_source = self.prepareSource(source)

        # Compile objects cannot be pickled
        self._v_compiled = CompiledProgram(self.__prepared_source,
                                           self.__filename())

    _tripleQuotedString = re.compile(
        r"^([ \t]*)[uU]?([rR]?)(('''|\"\"\")(.*)\4)", re.MULTILINE | re.DOTALL)

    def prepareSource(self, source):
        """Prepare source."""
        # compile() don't accept '\r' altogether
        source = source.replace("\r\n", "\n")
        source = source.replace("\r", "\n")
        
        if isinstance(source, unicode):

            # Use special conversion function to work around
            # compiler-module failure to handle unicode in literals

            try:
                source = source.encode('ascii')
            except UnicodeEncodeError:
                return self._tripleQuotedString.sub(_print_usrc, source)

        return self._tripleQuotedString.sub(r"\1print u\2\3", source)


    def getSource(self):
        """Get the original source code."""
        return self.__source

    # See IPythonPage
    source = property(getSource, setSource)


    def __call__(self, request, **kw):
        """See IPythonPage"""

        # Compile objects cannot be pickled
        if not hasattr(self, '_v_compiled'):
            self._v_compiled = CompiledProgram(self.__prepared_source,
                                               self.__filename())

        kw['request'] = request
        kw['script'] = self
        kw['context'] = zapi.getParent(self)

        interpreter = zapi.queryUtility(IInterpreter, 'text/server-python')
        return interpreter.evaluate(self._v_compiled, kw)

def _print_usrc(match):
    string = match.group(3)
    raw = match.group(2)
    if raw:
        return match.group(1)+'print '+`string`
    return match.group(1)+'print u'+match.group(3).encode('unicode-escape')

    
    
