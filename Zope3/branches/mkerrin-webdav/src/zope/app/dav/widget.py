##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Widgets specific to WebDAV

$Id$
"""
__docformat__ = 'restructuredtext'

from xml.dom import minidom

from zope.interface import implements
from zope.schema import getFieldNamesInOrder
from zope.schema.interfaces import ValidationError

from zope.app.datetimeutils import parseDatetimetz, DateTimeError
from zope.app.dav.interfaces import IDAVWidget
from zope.app.dav.opaquenamespaces import makeDOMStandalone

from zope.app.form import InputWidget
from zope.app.form.utility import setUpWidget
from zope.app.form.interfaces import MissingInputError, ConversionError, \
     WidgetsError, WidgetInputError

from zope.publisher.browser import TestRequest

class DAVWidget(InputWidget):
    """ DAV Widget """
    implements(IDAVWidget)

    _missing_value = object()

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.name = context.__name__

        self._xmldoc = minidom.Document()
        # field value
        self._value  = self._missing_value
        # input value has a xml dom node
        self._xmldom_value = self._missing_value

        self._error = None

        self.namespace = None
        self.ns_prefix = None

    def getErrors(self):
        return self._error

    def setNamespace(self, ns, ns_prefix):
        self.namespace = ns
        self.ns_prefix = ns_prefix

    def setRenderedValue(self, value):
        # don't use this
        self._value = value

    def applyChanges(self, content):
        return super(DAVWidget, self).applyChanges(content)

    def hasInput(self):
        return self._value is not self._missing_value or \
               self._xmldom_value is not self._missing_value

    def _getAndValidateInput(self):
        """get the input value contained within this widget in a valid format
        """
        field = self.context

        # form input is required, otherwise raise an error
        if not self.hasInput():
            raise MissingInputError(self.name, self.label, None)

        if self._xmldom_value is not self._missing_value:
            value = self._setFieldValue(self._xmldom_value)
        else:
            value = self._value

        # allow missing values only for non-required fields
        if value == field.missing_value: ## and not field.required:
            ## XXX - required is set all my fields and hence this is causing
            ## a problem.
            return value

        # value must be valid per the field constraints
        field.validate(value)

        return value

    def hasValidInput(self):
        try:
            self._getAndValidateInput()
            return True
        except (ConversionError, ValidationError):
            return False

    def getInputValue(self):
        self._error = None

        try:
            value = self._getAndValidateInput()
        except ConversionError, error:
            self._error = WidgetInputError(
                self.context.__name__, self.label, error)
            raise self._error
        except ValidationError, error:
            self._error = WidgetInputError(
                self.context.__name__, self.label, error)
            raise self._error

        return value

    def _toDAVValue(self, value):
        """Converts a field value to a string or a DOM Fragment to be used
        within the response of a WebDAV Request. This method can aslo return
        a lsit or tuple of DOM Fragments which can be used to 

        This method should be extended in order to correctly generate and
        take action on WebDAV requests.
        """
        if value:
            return str(value)
        return None

    def renderProperty(self, ns, ns_prefix):
        self.setNamespace(ns, ns_prefix)

        el = self._xmldoc.createElementNS(ns, self.name)
        if ns_prefix is not None:
            el.setAttributeNS(ns, 'xmlns', ns_prefix)

        # this is commented out because it cased some problems with values
        # being security proxied when they they are returned from the adapters
        ## value = self._toDAVValue(self.getInputValue())
        value = self._toDAVValue(self._value)

        if not value:
            return el
        elif not isinstance(value, tuple) and not isinstance(value, list):
            value = [value]

        for val in value:
            if isinstance(val, str) or isinstance(val, unicode):
                val = self._xmldoc.createTextNode(val)
            elif not isinstance(val, minidom.Node):
                raise WidgetsError(self._error, {self.name: val})

            el.appendChild(
                el.ownerDocument.importNode(val, True))

        return el

    def _setFieldValue(self, value):
        text = u''
        for node in value.childNodes:
            if node.nodeType != node.TEXT_NODE:
                continue
            text += node.nodeValue
        return text

    def setProperty(self, propel):
        self._xmldom_value = propel # self._setFieldValue(propel)


class TextDAVWidget(DAVWidget):
    """
    Renders a WebDAV property that contains text.

      >>> from zope.schema import Text
      >>> field = Text(__name__ = 'foo', title = u'Foo Title')
      >>> request = TestRequest()
      >>> widget = TextDAVWidget(field, request)

    Set up the value stored in the widget. In reality this is done in the
    setUpWidget method

      >>> widget.setRenderedValue(u'This is some content')
      >>> rendered = widget.renderProperty(None, None)
      >>> rendered #doctest:+ELLIPSIS
      <DOM Element: foo at 0x...>
      >>> rendered.toxml()
      '<foo>This is some content</foo>'

    """
    pass


class DatetimeDAVWidget(DAVWidget):
    """Render a WebDAV date property

      >>> from zope.schema import Datetime
      >>> field = Datetime(__name__ = 'foo', title = u'Foo Date Title')
      >>> request = TestRequest()
      >>> widget = DatetimeDAVWidget(field, request)

    Set the value of the widget to that of the current time. Use
    utcfromtimestamp in order for the test to pass in difference time zones.

      >>> from datetime import datetime
      >>> date = datetime.utcfromtimestamp(1131233651)
      >>> widget.setRenderedValue(date)
      >>> rendered = widget.renderProperty(None, None)
      >>> rendered #doctest:+ELLIPSIS
      <DOM Element: foo at ...>
      >>> rendered.toxml() # this was '<foo>2005-11-05 23:34:11Z</foo>'
      '<foo>Sat, 05 Nov 2005 23:34:11</foo>'

    """

    def _setFieldValue(self, value):
        if not value.childNodes:
            return self.context.missing_value

        value = value.childNodes[0]

        try:
            return parseDatetimetz(value.nodeValue)
        except (DateTimeError, ValueError, IndexError), v:
            raise ConversionError("Invalid datetime data", v)

    def _toDAVValue(self, value):
        if value is None:
            return None
        return value.strftime('%a, %d %b %Y %H:%M:%S %z').rstrip()


class CreatationDateDAVWidget(DAVWidget):
    """Render a WebDAV date property

      >>> from zope.schema import Datetime
      >>> field = Datetime(__name__ = 'foo', title = u'Foo Date Title')
      >>> request = TestRequest()
      >>> widget = CreatationDateDAVWidget(field, request)

    Set the value of the widget to that of the current time.

      >>> from datetime import datetime
      >>> date = datetime.utcfromtimestamp(1131233651)
      >>> widget.setRenderedValue(date)
      >>> rendered = widget.renderProperty(None, None)
      >>> rendered #doctest:+ELLIPSIS
      <DOM Element: foo at ...>
      >>> rendered.toxml()
      '<foo>2005-11-05T23:34:11Z</foo>'
    
    """

    def _setFieldValue(self, value):
        raise TypeError, "the creetion date is read-only"

    def _toDAVValue(self, value):
        if value is None:
            return None
        return value.strftime('%Y-%m-%dT%TZ')
    

class DateDAVWidget(DatetimeDAVWidget):
    """Render a WebDAV date property

      >>> from zope.schema import Datetime
      >>> field = Datetime(__name__ = 'foo', title = u'Foo Date Title')
      >>> request = TestRequest()
      >>> widget = DatetimeDAVWidget(field, request)

    Set the value of the widget to that of the current time.

      >>> from datetime import datetime
      >>> date = datetime.utcfromtimestamp(1131233651)
      >>> widget.setRenderedValue(date)
      >>> rendered = widget.renderProperty(None, None)
      >>> rendered #doctest:+ELLIPSIS
      <DOM Element: foo at ...>
      >>> rendered.toxml() # this was '<foo>2005-11-05 23:34:11Z</foo>'
      '<foo>Sat, 05 Nov 2005 23:34:11</foo>'

    """

    def _setFieldValue(self, value):
        if not value.childNodes:
            return self.context.missing_value

        value = value.childNodes[0]

        try:
            return parseDatetimetz(value.nodeValue).date()
        except (DateTimeError, ValueError, IndexError), v:
            raise ConversionError("Invalid date data", v)


class SequenceDAVWidget(DAVWidget):

    def _toDAVValue(self, value):
        if not value:
            return None
        string = ', '.join(value)
        return self._xmldoc.createTextNode(string)

    def _setFieldValue(self, value):
        text = u''
        for node in value.childNodes:
            if node.nodeType != node.TEXT_NODE:
                continue
            text += node.nodeValue
        return text.split(', ')


class ListDAVWidget(SequenceDAVWidget):
    pass


class TupleDAVWidget(SequenceDAVWidget):

    def _setFieldValue(self, value):
        value = super(TupleDAVWidget, self)._setFieldValue(value)

        return tuple(value)


class XMLEmptyElementListDAVWidget(DAVWidget):
    """
    This is a read-only widget.
    
      >>> from zope.schema import List
      >>> field = List(__name__ = 'foo', title = u'Foo Title')
      >>> request = TestRequest()
      >>> widget = XMLEmptyElementListDAVWidget(field, request)
      >>> widget.setRenderedValue(['first', 'second'])
      >>> rendered = widget.renderProperty(None, None)
      >>> rendered #doctest:+ELLIPSIS
      <DOM Element: foo at ...>
      >>> rendered.toxml()
      '<foo><first/><second/></foo>'
    """

    def _toDAVValue(self, value):
        if not value:
            return None

        res = []
        for item in value:
            el = self._xmldoc.createElementNS(self.namespace, str(item)) 
            res.append(el)
        return res

    def _setFieldValue(self, value):
        fvalue = []
        for node in value.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            fvalue.append(node.localName)
        return fvalue


class DAVXMLSubPropertyWidget(DAVWidget):

    def _toDAVValue(self, value):
        if value == None:
            return None
        
        mfield = self.context

        iface = mfield.schema
        pname = mfield.prop_name
        if pname:
            res = self._xmldoc.createElementNS(self.namespace, pname)
        else:
            res = []

        for fieldname in getFieldNamesInOrder(iface):
            field = iface[fieldname]
            setUpWidget(self, fieldname, field, IDAVWidget,
                        value = field.get(value),
                        ignoreStickyValues = False)
            widget = getattr(self, fieldname + '_widget', None)
            assert widget is not None
            ## namespace information is not needed here since we set the
            ## default namespace on elements
            el = widget.renderProperty(self.namespace, self.ns_prefix)
            if pname:
                res.appendChild(el)
            else:
                res.append(el)

        return res


class DAVOpaqueWidget(DAVWidget):

    def renderProperty(self, ns, ns_prefix):
        self.setNamespace(ns, ns_prefix)
        
        value = self.getInputValue()
        if value == self.context.missing_value:
            el = self._xmldoc.createElementNS(ns, self.name)
            if ns_prefix is not None:
                el.setAttributeNS(ns, 'xmlns', ns_prefix)
            return el
        el = minidom.parseString(value)

        el = el.documentElement

        if ns_prefix is not None and el.attributes is not None:
            xmlns = el.attributes.getNamedItem('xmlns')
            if xmlns is None:
                el.setAttributeNS(ns, 'xmlns', ns_prefix)

        return el

    def _setFieldValue(self, value):
        el = makeDOMStandalone(value)

        return el.toxml()
