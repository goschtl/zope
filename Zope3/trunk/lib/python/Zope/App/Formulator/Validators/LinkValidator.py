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

$Id: LinkValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from StringValidator import StringValidator


class LinkHelper:
    """A helper class to check if links are openable.
    """
    status = 0

    def __init__(self, link):
        self.link = link
        
    def open(self):
        try:
            urlopen(self.link)
        except:
            # all errors will definitely result in a failure
            pass
        else:
            # FIXME: would like to check for 404 errors and such?
            self.status = 1


class LinkValidator(StringValidator):
    """ """

    propertyNames = StringValidator.propertyNames +\
                     ['checkLink', 'checkTimeout', 'linkType']
    
    checkLink = 0
    checkTimeout = 7.0
    linkType = "external"
    
    messageNames = StringValidator.messageNames + ['notLink']
    
    notLink = 'The specified link is broken.'
    
    def validate(self, field, value):
        value = StringValidator.validate(self, field, value)
        if value == "" and not field.get_value('required'):
            return value
        
        linkType = field.get_value('linkType')
        if linkType == 'internal':
            value = urljoin(REQUEST['BASE0'], value)
        elif linkType == 'relative':
            value = urljoin(REQUEST.URL[-1], value)
        # otherwise must be external

        # FIXME: should try regular expression to do some more checking here?
        
        # if we don't need to check the link, we're done now
        if not field.get_value('checkLink'):
            return value

        # check whether we can open the link
        link = LinkHelper(value)
        thread = Thread(target=link.open)
        thread.start()
        thread.join(field.get_value('checkTimeout'))
        del thread
        if not link.status:
            self.raise_error('notLink', field)
            
        return value
