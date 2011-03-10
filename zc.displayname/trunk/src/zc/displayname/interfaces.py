##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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

"""site interfaces

$Id: interfaces.py 3161 2005-07-27 21:49:58Z fred $
"""
from zope import interface

class IDisplayNameGenerator(interface.Interface):
    def __call__(maxlength=None):
        """return a display name for this object.
        
        if length is None, length is not constrained.  If maxlength is an
        integer, the display may be up to that number of characters.
        
        Implementations may refuse to support maxlengths smaller than a
        minimum value by raising ValueError; raise ValueError if maxlength < 0.
        
        Depending on the type of request for which the name generator is used,
        the display name may include (well-formed) XML such as XHTML.
        Name generators registered for IRequest should not include any such
        extra content.  If a display name generator for an IBrowserRequest
        has a maxlength, the maxlength should not include the length of the
        XML tags.
        """

class IBreadcrumbs(interface.Interface):
    def __call__(maxlength=None):
        """return a sequence of dictionaries with breadcrumb information.
        
        Each dictionary has four keys: name, url, object, and name_gen.
        
        name: a display name for the breadcrumbs, truncated with maxlength
              as passed to an IDisplayNameGenerator.
        
        url: the traversed url for the object.
        
        object: the object (available for getting other information such as
                an icon).
        
        name_gen: an IDisplayNameGenerator for the object.
        
        Objects are free to not include themselves in breadcrumbs.
        
        Breadcrumbs stop at the virtual host root, if any.
        """
