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
$Id: metametaConfigureForDocgen.py,v 1.3 2002/11/08 19:08:27 rdmurray Exp $
"""
from metametaConfigure import DirectiveNamespace as baseDirectiveNamespace
from metametaConfigure import Subdirective as baseSubdirective
from INonEmptyDirective import INonEmptyDirective
from ISubdirectiveHandler import ISubdirectiveHandler

#
# Versions of the meta configuration directive handlers that save the
# documentation information as structured data.
#

"""
To track the meta-data about configuration directives, we use a
special key that will never appear as an actual subdirective name.
So the information stored under that key in a (sub)directive's
subdirective registry is the meta data about the (sub)directive
itself.

That data consists of a dictionary with the following keys:

description -- a description of the (sub)directive.  It should
    explain the semantics of the (sub)directive.

attributes -- a dictionary containing entries for each attribute
    the (sub)command accepts.  The value of the entries in this
    dictionary are dictionaries with the following keys:

    description -- a description of the attribute.  It should
        explain the semantics of the attribute.

    required -- 'yes', 'no', or ''.  Applies to attributes
        and means what it sounds like it means.  Blank is
        more or less equivalent to except that an attribute
        with a blank required might be one that is a member of a
        set *one* of which is required, while if an explicit
        'no' is given then the attribute is completely optional.
        This information will be included in the generated doc strings.

This metadata is intended to serve as the most basic level of documentation
of the directives, and should be updated along with the directive code
(which is why it is stored in the meta.zcml file).  The metadata should
be extracted and made human accessible by a zope-independent program
and/or a zope-based introspection tool.
"""
_metadataKey = "__Zope.Configuration.metadataKey__"

def _recordCommandMetadata(subs, description, handler=None):
        if _metadataKey not in subs: subs[_metadataKey] = {}
        md = subs[_metadataKey]
        if 'attributes' not in md: md['attributes'] = {}
        if description: md['description'] = ' '.join(description.split())
        if handler: md['handler'] = handler


class DirectiveNamespace(baseDirectiveNamespace):
    """An extended class that handles descriptions and attributes"""

    __class_implements_ = INonEmptyDirective
    __implements__ = ISubdirectiveHandler

    def _Subdirective(self, *args, **kw): return Subdirective(*args, **kw)

    def _useDescription(self, namespace, name, handler, description, subs):
        _recordCommandMetadata(subs, description, handler)


class Subdirective(baseSubdirective):
    """An extended class that handles descriptions and attributes"""

    __implements__ = ISubdirectiveHandler

    def _useDescription(self, namespace, name, subs, description):
        _recordCommandMetadata(subs, description)

    def _useAttributeDescription(self, name, required, description):
        attribs = self._subs[_metadataKey]['attributes']
        attribs[name] = {
            'description': description and ' '.join(description.split()),
            'required': required}
