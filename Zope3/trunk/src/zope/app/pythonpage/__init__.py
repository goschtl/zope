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
"""Python Page

$Id: __init__.py,v 1.8 2004/04/02 17:07:59 tim_one Exp $
"""
import re
from persistent import Persistent
from zope.app import zapi
from zope.app.container.contained import Contained
from zope.app.interpreter.interfaces import IInterpreter
from zope.component.servicenames import Utilities
from zope.interface import Interface, implements
from zope.schema import SourceText, TextLine
from zope.app.i18n import ZopeMessageIDFactory as _

triple_quotes_start = re.compile('^[ \t]*("""|\'\'\')', re.MULTILINE)
single_triple_quotes_end = re.compile("'''")
double_triple_quotes_end = re.compile('"""')

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
        required=False)

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

      Make sure that Windows (\r\n) line ends also work.

      >>> pp.setSource(u"if 1 == 1:\r\n\r\n   '''<html>...</html>'''")
      >>> pp(request)
      u'<html>...</html>\n'

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

      >>> try:
      ...     pp.setSource(u"'''<html>...</html>") #'''"
      ... except SyntaxError, err:
      ...     print err
      No matching closing quotes found. (line 1)

      # XXX: Note: We cannot just print the error directly, since there is a
      # bug in the Linux version of Python that does not display the filename
      # of the source correctly. So we construct an information string by hand.

      >>> try:
      ...     pp.setSource(u"prin 'hello'")
      ... except SyntaxError, err:
      ...     err_dict = err.__dict__
      ...     print '%(filename)s, line %(lineno)i, offset %(offset)i' %err_dict
      /pp, line 1, offset 12
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

        source = source.encode('utf-8')
        # compile() don't accept '\r' altogether
        source = source.replace("\r\n", "\n")
        source = source.replace("\r", "\n")
        start = 0
        match = triple_quotes_start.search(source, start)
        while match:
            open = match.group()
            source = source[:match.end()-3] + 'print u' + \
                     source[match.end()-3:]
            start = match.end() + 7

            # Now let's find the end of the quote
            if match.group().endswith('"""'):
                end = double_triple_quotes_end.search(source, start)
            else:
                end = single_triple_quotes_end.search(source, start)

            if end is None:
                lineno = len(source[:start].split('\n'))
                offset = len(match.group())
                raise SyntaxError(
                    'No matching closing quotes found.',
                    (self.__filename(), lineno, offset, match.group()))

            start = end.end()
            match = triple_quotes_start.search(source, start)

        self.__prepared_source = source

        # Compile objects cannot be pickled
        self._v_compiled = compile(self.__prepared_source, self.__filename(),
                                   'exec')

    def getSource(self):
        """Get the original source code."""
        return self.__source

    # See IPage
    source = property(getSource, setSource)


    def __call__(self, request, **kw):
        """See IPythonPage"""

        # Compile objects cannot be pickled
        if not hasattr(self, '_v_compiled'):
            self._v_compiled = compile(self.__prepared_source,
                                       self.__filename(), 'exec')

        kw['request'] = request
        kw['script'] = self
        kw['context'] = zapi.getParent(self)

        service = zapi.getService(self, Utilities)
        interpreter = service.queryUtility(IInterpreter,
                                           name='text/server-python')
        return interpreter.evaluate(self._v_compiled, kw)
