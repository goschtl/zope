##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""A collection of tools to support the ZSCP file formats.

$Id$
"""
__docformat__ = "reStructuredText"
import re
from distutils.util import rfc822_escape
from email.Parser import HeaderParser
from xml.sax import make_parser
from xml.sax.xmlreader import InputSource
from xml.sax.handler import ContentHandler
from cStringIO import StringIO

import zope.schema
from zope.pagetemplate import pagetemplatefile

def getHeaderName(name):
    """Convert field names to RFC 2822 header names."""
    parts = re.findall('^[a-z]+|[A-Z][a-z0-9]+', name)
    headerName = '-'.join(part.lower() for part in parts)
    return headerName.capitalize()

def getFieldName(name):
    """Convert XML element names to field names."""
    name = name.lower()
    parts = name.split('-')
    name = ''.join([part.capitalize() for part in parts])
    return name[0].lower() + name[1:]

def rfc822_unescape(value):
    return value.replace('\n        ', '\n')


class XMLStructuralError(Exception):
    """An exception that represents an error in the XML structure."""

    def __init__(self, locator):
        self.locator = locator

    def __str__(self):
        return '(file "%s", line %s, column %s)'% (
            self.locator.getSystemId(),
            self.locator.getLineNumber(),
            self.locator.getColumnNumber())


class RequiredElementsMissing(XMLStructuralError):
    """A required field is missing."""

    def __init__(self, elementName, names, locator):
        XMLStructuralError.__init__(self, locator)
        self.elementName = elementName
        self.names = names

    def __str__(self):
        info = XMLStructuralError.__str__(self)
        return 'Required field(s) %s missing in `%s` %s' % (
            ', '.join([name.__repr__() for name in self.names]),
            self.elementName,
            info)


class InvalidSubElement(XMLStructuralError):
    """An unsuspected sub-element was found."""

    def __init__(self, fieldName, locator):
        XMLStructuralError.__init__(self, locator)
        self.fieldName = fieldName

    def __str__(self):
        info = XMLStructuralError.__str__(self)
        return '`%s` cannot have sub-elements %s' %(self.fieldName, info)


class XMLHandler(ContentHandler):
    """A SAX event handler that creates a Python object from the XML events
    using a schema.
    """

    def __init__(self, rootElementName, rootElementField, factories):
        self.stack = []
        self.root = None
        self.rootElementName = rootElementName
        self.rootElementField = rootElementField
        self.factories = factories

    @property
    def current(self):
        return self.stack[-1]

    def _verifyComplexElement(self, obj, iface, elemName):
        missingFields = []
        for name, field in zope.schema.getFields(iface).items():
            if field.required and getattr(obj, name) == field.missing_value:
                if field.default is not field.missing_value:
                    setattr(obj, name, field.default)
                else:
                    missingFields.append(name)
        if missingFields:
            raise RequiredElementsMissing(
                elemName, sorted(missingFields), self.locator)

    def setDocumentLocator(self, locator):
        self.locator = locator

    def characters(self, text):
        if isinstance(self.current[0], unicode):
            self.current[0] += text

    def startElement(self, name, attrs):
        attrName = getFieldName(name)

        if not self.stack:
            if name != self.rootElementName:
                raise ValueError(
                    'The root element must be named `%s`' %self.rootElementName)
            field = self.rootElementField
        else:
            currentField = self.current[1]
            if zope.schema.interfaces.IObject.providedBy(currentField):
                field = currentField.schema.getDescriptionFor(attrName)
            elif zope.schema.interfaces.IList.providedBy(currentField):
                field = currentField.value_type
            else:
                raise InvalidSubElement(currentField.__name__, self.locator)

        if zope.schema.interfaces.IObject.providedBy(field):
            obj = self.factories[field.schema](**dict(attrs))
        elif zope.schema.interfaces.IList.providedBy(field):
            obj = []
        else:
            obj = u''

        self.stack.append([obj, field])


    def endElement(self, name):
        attrName = getFieldName(name)

        obj, field = self.stack.pop()
        if zope.schema.interfaces.IObject.providedBy(field):
            self._verifyComplexElement(obj, field.schema, name)
        elif zope.schema.interfaces.IList.providedBy(field):
            pass
        else:
            obj = field.fromUnicode(obj.strip())

        if not self.stack:
            self.root = obj
        elif zope.schema.interfaces.IList.providedBy(self.current[1]):
            self.current[0].append(obj)
        else:
            setattr(self.current[0], attrName, obj)


def processXML(file, handler):
    """Read the releases XML string."""
    src = InputSource(getattr(file, 'name', '<string>'))
    src.setByteStream(file)
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.parse(src)
    return handler.root


def _listHandler(producer, obj, field):
    return [producer.produce(entry, field.value_type)
            for entry in obj]

def _objectHandler(producer, obj, field):
    info = {}
    for name, field in zope.schema.getFieldsInOrder(field.schema):
        info[name] = producer.produce(getattr(obj, name), field)
    return info


class InfoProducer(object):
    """An object that produces a TAL-friendly info object from an obejct using
    a schema.
    """

    handlers = {zope.schema.interfaces.IList: _listHandler,
                zope.schema.interfaces.IObject: _objectHandler}

    def __init__(self, rootObject, rootField):
        self.rootObject = rootObject
        self.rootField = rootField

    def produce(self, obj, field):
        if obj is None:
            return None

        for fieldIface, handler in self.handlers.items():
            if fieldIface.providedBy(field):
                return handler(self, obj, field)

        return str(obj)

    def __call__(self):
        return self.produce(self.rootObject, self.rootField)


def produceXML(producer, template):
    return pagetemplatefile.PageTemplateFile(template)(root=producer())


class HeaderProcessor(object):
    """Parses RFC 2822 style headers into a Python object using a schema."""

    def __init__(self, root, schema):
        self.root = root
        self.schema = schema
        self.missingRequired = []

    def _getHeaderName(self, name):
        parts = re.findall('^[a-z]+|[A-Z][a-z0-9]+', name)
        headerName = '-'.join(part.lower() for part in parts)
        return headerName.capitalize()

    def _processSingleHeader(self, name, field):
        headerName = getHeaderName(name)
        headers = self.msg.get_all(headerName)
        if headers and len(headers) > 1:
            raise ValueError("header %r can only be given once" % headerName)
        if headers:
            value = unicode(headers[0])
            setattr(self.root, name,
                    field.fromUnicode(rfc822_unescape(value)))
        else:
            if field.missing_value != field.default:
                setattr(self.root, name, field.default)
            elif field.required:
                self.missingRequired.append(headerName)

    def _processMultiHeader(self, name, field):
        headerName = getHeaderName(name)
        headers = self.msg.get_all(headerName)
        if headers:
            values = [
                field.value_type.fromUnicode(rfc822_unescape(unicode(value)))
                for value in headers]
            setattr(self.root, name, values)
        else:
            if field.missing_value != field.default:
                setattr(self.root, name, field.default)
            elif field.required:
                self.missingRequired.append(headerName)

    def __call__(self, file):
        parser = HeaderParser()
        self.msg = parser.parse(file)
        for name, field in zope.schema.getFieldsInOrder(self.schema):
            if zope.schema.interfaces.IList.providedBy(field):
                self._processMultiHeader(name, field)
            else:
                self._processSingleHeader(name, field)

        if self.missingRequired:
            raise ValueError('Required headers missing: %s' %
                             ', '.join(self.missingRequired))


class HeaderProducer(object):
    """Produces a RFC 2822 style header string from a Python object using a
    schema.
    """

    def __init__(self, root, schema):
        self.root = root
        self.schema = schema

    def _produceMultiHeader(self, name, value, field):
        for subvalue in value:
            self._produceSingleHeader(name, subvalue, field.value_type)

    def _produceSingleHeader(self, name, value, field):
        headerName = getHeaderName(name)
        if isinstance(value, unicode):
            value = value.encode('utf8')
        value = rfc822_escape(str(value))
        self.output.write('%s: %s\n' %(headerName, value))

    def __call__(self):
        self.output = StringIO()
        for name, field in zope.schema.getFieldsInOrder(self.schema):
            value = getattr(self.root, name)
            if value == field.missing_value:
                continue
            if zope.schema.interfaces.IList.providedBy(field):
                self._produceMultiHeader(name, value, field)
            else:
                self._produceSingleHeader(name, value, field)
        return self.output.getvalue()
