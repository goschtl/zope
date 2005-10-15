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
"""HTML fragement encoding sniffer

$Id$
"""
 
from HTMLParser import HTMLParser 
from HTMLParser import HTMLParseError

class EncodingFound(Exception):
    # This exception is throwned by the parser when a meta tag with
    # charset is found. The value attribute holds the charset.
    def __init__(self, value):
        self.value = value

class EncodingParser(HTMLParser):
    """Encoding Parser for HTML fragments
    """
    def handle_starttag(self, tag, attrs):
        # This method is called to handle the start of a tag If it founds
        # a meta tag with charst information it raises an EncodingFound
        # exception holding the charset
        if tag != 'meta':
            return
        for attr, value in attrs:
            if (attr == 'content' and
                'charset' in value):
                try:
                    charset = value.split(';')[1].split('=')[1]
                except IndexError:
                    pass
                else:
                    raise EncodingFound(charset)

def sniff_encoding(data):
    """Try to sniff the encoding of an HTML fragment by checking the
    meta tag and the charset information
    """
    parser = EncodingParser()
    try:
        parser.feed(data)
    except EncodingFound, e:
        return e.value.strip()
    except HTMLParseError:
        pass
    return ''
