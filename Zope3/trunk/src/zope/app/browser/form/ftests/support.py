##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id: support.py,v 1.4 2004/03/02 18:27:37 philikon Exp $
"""

import re
from zope.configuration import xmlconfig

def registerEditForm(schema):
    xmlconfig.string("""
        <configure xmlns="http://namespaces.zope.org/browser">
          <include package="zope.app.browser.form" file="meta.zcml" />
          <editform
            name="edit.html"
            schema="%s"
            permission="zope.View" />
        </configure>
        """ % schema.__identifier__)


def defineSecurity(class_, schema):
    class_ = '%s.%s' % (class_.__module__, class_.__name__)
    schema = schema.__identifier__
    xmlconfig.string("""
        <configure xmlns="http://namespaces.zope.org/zope">
          <include package="zope.app.component" file="meta.zcml" />
          <class class="%s">
            <require
              permission="zope.Public"
              interface="%s"
              set_schema="%s" />
          </class>
        </configure>
        """ % (class_, schema, schema))


def defineWidgetView(name, field_interface, widget_class):
    field_interface = field_interface.__identifier__
    widget_class = '%s.%s' % (widget_class.__module__, widget_class.__name__)
    xmlconfig.string("""
        <configure xmlns="http://namespaces.zope.org/browser">
          <include package="zope.app.publisher.browser" file="meta.zcml" />
          <page
            name="%s"
            permission="zope.Public"
            allowed_interface="zope.app.browser.interfaces.form.IBrowserWidget"
            for="%s"
            class="%s" />
        </configure>
        """ % (name, field_interface, widget_class))


def patternExists(pattern, source, flags=0):
    return re.search(pattern, source, flags) is not None


def validationErrorExists(field, error_msg, source):
    return patternExists(
        'name="field.%s".*%s' % (field, error_msg), source)


def missingInputErrorExists(field, source):
    return validationErrorExists(field, 'Input is required', source)


def invalidValueErrorExists(field, source):
    # assumes this error is displayed for select elements
    return patternExists(
        'name="field.%s".*</select>.*Invalid value' % field,
        source, re.DOTALL)


def updatedMsgExists(source):
    return patternExists('<p>Updated .*</p>', source)
