##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""XML differences for use in testing the WebDAV code base

$Id:$
"""
__docformat__ = 'restructuredtext'

from xml.dom import minidom

def getTextNode(self, el):
    value = None
    for node in el.childNodes:
        if node.nodeType != node.TEXT_NODE:
            continue
        self.assert_(value is None)
        value = node.nodeValue
    return value

def convertToDict(self, ms):
    responses = {}

    for response in ms.childNodes:
        self.assertEqual(response.localName, 'response')

        hrefel = response.getElementsByTagNameNS('DAV:', 'href')
        self.assertEqual(len(hrefel), 1)
        href = getTextNode(self, hrefel[0])
        self.assert_(responses.has_key(href) is False)
        propstats = responses[href] = {}

        for propstat in response.getElementsByTagNameNS('DAV:', 'propstat'):
            statusel = propstat.getElementsByTagNameNS('DAV:', 'status')
            self.assertEqual(len(statusel), 1)
            status = getTextNode(self, statusel[0])
            properties = propstats[status] = {}
            propel = propstat.getElementsByTagNameNS('DAV:', 'prop')
            self.assertEqual(len(propel), 1)

            for propertyel in propel[0].childNodes:
                if propertyel.nodeType != propertyel.ELEMENT_NODE:
                    continue
                ns = propertyel.namespaceURI
                propname = propertyel.localName
                value = propertyel.toxml()

                nsprops = properties.setdefault(ns, {})
                nsprops[propname] = value

    return responses

def compareMultiStatus(self, status1str, status2str):
    s1 = minidom.parseString(status1str)
    s2 = minidom.parseString(status2str)

    ms1 = s1.documentElement
    ms2 = s2.documentElement

    self.assertEqual(ms1.localName, 'multistatus')
    self.assertEqual(ms2.localName, 'multistatus')

    resp1 = convertToDict(self, ms1)
    resp2 = convertToDict(self, ms2)

    self.assertEqual(len(resp1), len(resp2))
    for href, status1 in resp1.items():
        self.assert_(resp2.has_key(href),
                     "the expected result is missing a response for the" \
                     " %s object\n" \
                     "'%s' != '%s'" % (href, status1str, status2str))
        status2 = resp2[href]

        for status, namespaces1 in status1.items():
            self.assert_(status2.has_key(status))
            namespaces2 = status2[status]

            self.assertEqual(len(namespaces1), len(namespaces2),
                             "namespace count doesn't match." \
                             "'%s' != '%s'" %(status1str, status2str))
        
            for namespace, properties1 in namespaces1.items():
                self.assert_(namespaces2.has_key(namespace),
                             "the namespace %s is missing from the " \
                             " expected result.\n" \
                             "'%s' != '%s'" % (namespace, status1str,
                                               status2str))
                properties2 = namespaces2[namespace]

                self.assertEqual(len(properties1), len(properties2))

                for propname, value1 in properties1.items():
                    self.assert_(properties2.has_key(propname),
                                 "the property %s is missing from the " \
                                 "expected result" % propname)
                    value2 = properties2[propname]

                    self.assertEqual(value1, value2)
