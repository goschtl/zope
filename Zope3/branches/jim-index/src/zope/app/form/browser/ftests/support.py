##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Support Functions for Widget Functional Tests

$Id$
"""
import re
from zope.configuration import xmlconfig

def registerEditForm(schema):
    xmlconfig.string("""
        <configure xmlns="http://namespaces.zope.org/browser">
          <include package="zope.app.form.browser" file="meta.zcml" />
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


def defineWidgetView(field_interface, widget_class, view_type):
    field_interface = field_interface.__identifier__
    widget_class = '%s.%s' % (widget_class.__module__, widget_class.__name__)
    view_type = '%s.%s' % (view_type.__module__, view_type.__name__)
    xmlconfig.string("""
        <configure xmlns="http://namespaces.zope.org/zope">
          <include package="zope.app.component" file="meta.zcml" />
          <view
            for="%s"
            type="zope.publisher.interfaces.browser.IBrowserRequest"
            factory="%s"
            provides="%s"
            permission="zope.Public"
            />
        </configure>
        """ % (field_interface, widget_class, view_type))


def patternExists(pattern, source, flags=0):
    return re.search(pattern, source, flags) is not None


def validationErrorExists(field, error_msg, source):
    return patternExists(
        'name="field.%s".*%s' % (field, error_msg), source, re.DOTALL)


def missingInputErrorExists(field, source):
    return validationErrorExists(field, 'Required input is missing.', source)


def invalidValueErrorExists(field, source):
    # assumes this error is displayed for select elements
    return patternExists(
        'name="field.%s".*</select>.*Invalid value' % field,
        source, re.DOTALL)


def updatedMsgExists(source):
    return patternExists('<p>Updated .*</p>', source)
