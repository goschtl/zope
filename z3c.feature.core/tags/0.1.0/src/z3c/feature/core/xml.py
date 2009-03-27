##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""XML Processing

$Id$
"""

from lxml import etree
import types
import pkg_resources
from zc.buildout import easy_install
from zope.interface import directlyProvides

from z3c.builder.core import project, base
from z3c.feature.core import interfaces

target_dir = pkg_resources.working_set.find(
    pkg_resources.Requirement.parse('zc.buildout')).location


class FeatureDocBuilder(base.FileBuilder):
    """A builder to document all applied features of a project."""

    def render(self):
        result = open(
            base.getTemplatePath('zboiler-doc-header.txt'), 'r').read()
        for feature in self.getProject().appliedFeatures:
            title = feature.featureTitle
            result += "\n\n" + title + "\n"
            result += "-"*len(title) + "\n"
            docs = feature.featureDocumentation.strip()
            result += "\n" + docs + "\n\n"
        return result


def getNode(nodeOrFileOrStr):
    if isinstance(nodeOrFileOrStr, types.StringTypes):
        return etree.fromstring(nodeOrFileOrStr)
    elif hasattr(nodeOrFileOrStr, 'read'):
        data = nodeOrFileOrStr.read()
        nodeOrFileOrStr.seek(0)
        return etree.fromstring(data)
    elif isinstance(nodeOrFileOrStr, etree._Element):
        return nodeOrFileOrStr
    else:
        raise TypeError("Could not get a lxml.etree.Element "
                        "object from %s" % nodeOrFileOrStr)

def getFeatureFactory(featureNode):
    featureType = featureNode.get('type')
    egg, entryPoint = featureType.split(':')
    if egg not in pkg_resources.working_set.by_key:
        ws = easy_install.install([egg], target_dir, newest=True)
        distro = ws.find(pkg_resources.Requirement.parse(eggs))
        pkg_resources.working_set.add(distro)
    else:
        distro = pkg_resources.get_distribution(egg)
    try:
        featureFactory = distro.load_entry_point(
            interfaces.FEATURE_GROUP, entryPoint)
    except ImportError, e:
        raise ValueError("Unable to load feature factory for %s:%s because: %s" % (interfaces.FEATURE_GROUP, entryPoint, e))
    return featureFactory

def getFeaturesDict(node):
    node = getNode(node)
    features = {}
    for featureNode in node.xpath('//feature'):
        featureFactory = getFeatureFactory(featureNode).fromXMLNode(featureNode)
        feature = featureFactory.fromXMLNode(featureNode)
        features[featureNode.get('type')] = feature
    return features

def getFeatures(node):
    return getFeaturesDict(node).values()


def xmlToProject(node):
    node = getNode(node)
    name = node.get("name")
    builder = project.BuildoutProjectBuilder(unicode(name))
    from z3c.feature.core import base
    base.applyFeatures(getFeatures(node), builder)
    builder.add(FeatureDocBuilder(u'ZBOILER.txt'))
    return builder

def extractData(node, iface, convert=True):
    node = getNode(node)
    data = {}
    for fieldName in iface:
        matches = node.xpath('./%s'%fieldName.replace('_','-'))
        match = matches[0] if matches else None
        if match is not None:
            if convert:
                # ignore templated values when converting to actual fields.
                if match.text == "?":
                    continue
                # see if this is a composite element representing a list of
                # items.
                items = match.xpath('./item')
                if items:
                    data[fieldName] = [unicode(item.text) for item in items]
                # otherwise, see if we can parse a value from unicode
                elif hasattr(iface[fieldName], 'fromUnicode'):
                    data[fieldName] = iface[fieldName].fromUnicode(
                        unicode(match.text))
                # oh well, we'll just send back the unicode and hope that's ok
                elif match.text:
                    data[fieldName] = unicode(match.text)
            else:
                data[fieldName] = unicode(match.text)
    return data
