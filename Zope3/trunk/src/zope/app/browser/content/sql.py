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
"""SQL Script Views

$Id: sql.py,v 1.12 2003/12/16 15:41:59 mchandra Exp $
"""

from zope.app.browser.form.add import AddView
from zope.app.browser.form.submit import Update
from zope.app.interfaces.content.sql import ISQLScript
from zope.app.interfaces.rdb import DatabaseException
from zope.app.interfaces.container import IAdding
from zope.app.content.sql import SQLScript
from zope.app import zapi

class SQLScriptTest:
    """Test the SQL inside the SQL Script"""

    __used_for__ = ISQLScript

    error = None

    def getArguments(self):
        form = self.request.form
        arguments = {}

        for argname, argvalue in self.context.getArguments().items():
            value = form.get(argname)
            if value is None:
                value = argvalue.get('default')
            if value is not None:
                arguments[argname.encode('UTF-8')] = value
        return arguments

    def getTestResults(self):
        try:
            return self.context(**self.getArguments())
        except (DatabaseException, AttributeError, Exception), error:
            self.error = error
            return []

    def getFormattedError(self):
        error = str(self.error)
        return error

    def getRenderedSQL(self):
        return self.context.getTemplate()(**self.getArguments())



class SQLScriptAdd(object):
    """Provide interface to add SQL Script """
     
        
    def update(self):
        """ Set the Update variable for Add and Test
        >>> from zope.publisher.browser import TestRequest
        
        >>> rqst = TestRequest()
        >>> class Base(object):
        ...     def __init__(self, request):
        ...         self.request = request
        ...     def update(self):
        ...         self.updated = 1
         
        >>> class V(SQLScriptAdd, Base):
        ...     pass
        
        >>> dc = V(rqst)
        >>> res = 0
        >>> dc.update()
        >>> dc.updated
        1
        >>> 'UPDATE_SUBMIT' in rqst
        False
        >>> d = {'add_test':1}
        >>> rqst1 = TestRequest(form = d)
        >>> dc1 = V(rqst1)
        >>> dc1.update()
        >>> 'UPDATE_SUBMIT' in rqst1
        True
        """
        if 'add_test' in self.request:
            self.request.form[Update] = ''
            
        return super(SQLScriptAdd, self).update()
        
              
    def nextURL(self):
        """
        >>> from zope.publisher.browser import TestRequest
        >>> from zope.app.tests.placelesssetup import setUp, tearDown
        >>> setUp()
        >>> rqst = TestRequest()
        >>> class Base(object):
        ...     def __init__(self, request):
        ...         self.request = request
        ...         self.context = self
        ...         self.contentName = 'new srcipt'
        ...     def __getitem__(self, key):
        ...         return None
        ...     def nextURL(self):
        ...         return "www.zeomega.com"
        
        >>> class V(SQLScriptAdd, Base):
        ...     pass
        >>> 
        >>> rqst = TestRequest()
        >>> dc = V(rqst)
        >>> dc.nextURL()
        'www.zeomega.com'
        >>> d = {'add_test':1}
        >>> rqst1 = TestRequest(form = d)
        >>> dc1 = V(rqst1)
        >>> dc1.nextURL()
        'http://127.0.0.1/test.html'

        """


        if 'add_test' in self.request:
            name = self.context.contentName
            container = self.context.context
            obj = container[name]
            url = zapi.getView(obj, 'absolute_url', self.request)()
            url = '%s/test.html' % url
            return url
        else:
            return super(SQLScriptAdd, self).nextURL()
       
        
        

    
    
