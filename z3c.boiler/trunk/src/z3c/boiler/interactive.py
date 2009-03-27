##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Interactive CLI

$Id$
"""
import logging
from z3c.feature.core import xml, template
from z3c.feature.core.xml import etree
from z3c.builder.core import project, base
from z3c.feature.core.base import getFeatureSchema
from zope.schema import List

def prompt(field):
    promptText = field.title
    if field.default:
        promptText += " [%s]" % field.default
    if field.description:
        promptText += " (? for help)"
    promptText += ": "

    nonSubmitValues = {}
    if field.description:
        nonSubmitValues['?'] = field.description

    def getResponse(value):
        while value in nonSubmitValues.keys():
            print nonSubmitValues[value]
            value = raw_input(promptText)
        return unicode(value)

    if hasattr(field, 'fromUnicode'):
        if field.required and not field.default:
            nonSubmitValues[""] = "Sorry, but this field is required."

        value = getResponse(raw_input(promptText))
        if value == "" and field.default:
            print "using default value: %s" % field.default
            value = field.default
        if value != "":
            value = field.fromUnicode(value)
    elif isinstance(field, List):
        valueList = []
        value = None
        while value != "":
            value = getResponse(raw_input(promptText))
            if value:
                valueList.append(value)
        value = valueList
    else:
        base.logger.warn("Not sure how to convert field: %s" % field)
        value = unicode(value)
    return value

def xmlToProject(node):
    originalNode = node
    node = xml.getNode(node)
    name = raw_input("Enter the name for this project: ").strip()
    while name == "":
        print "You must provide a name for your project."
        name = raw_input("Enter the name for this project: ").strip()
    node.set('name',name)

    # fill in missing xml by prompting
    for featureNode in node.xpath('//feature'):
        factory = xml.getFeatureFactory(featureNode)
        schema = getFeatureSchema(factory)
        data = xml.extractData(featureNode, schema, convert=False)
        fieldNames = [n for n in schema if data.get(n) == '?']
        if fieldNames:
            print ""
            header = "Options for: "+featureNode.get("type")
            print header
            print "-"*len(header)
        for fieldName in fieldNames:
            fieldValue = prompt(schema[fieldName])
            fieldNode = featureNode.xpath('./%s' % fieldName.replace('_','-'))[0]
            if isinstance(fieldValue, unicode):
                fieldNode.text = fieldValue
            elif isinstance(fieldValue, list):
                fieldNode.text = None
                for item in fieldValue:
                    itemNode = etree.SubElement(fieldNode, "item")
                    itemNode.text = item
    print
    print "Finished creating xml definition."
    print
    if raw_input("Do you want to see the generated xml definition? (y/[n]): ") == 'y':
        print etree.tostring(node, pretty_print=True)
        if raw_input("Does this look right? ([y]/n): ") == 'n':
            print
            raw_input("Ok, we'll start over.")
            print
            print '-'*78
            print
            return xmlToProject(originalNode)
    return xml.xmlToProject(node)

