##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
'''This module implements a simple item mix-in for objects that have a
very simple (e.g. one-screen) management interface, like documents,
Aqueduct database adapters, etc.

This module can also be used as a simple template for implementing new
item types. 

$Id: SimpleItem.py,v 1.100 2002/06/12 18:34:17 shane Exp $'''
__version__='$Revision: 1.100 $'[11:-2]

import re, sys, Globals, App.Management, Acquisition, App.Undo
import AccessControl.Role, AccessControl.Owned, App.Common
from webdav.Resource import Resource
from ExtensionClass import Base
from CopySupport import CopySource
from types import InstanceType, StringType
from ComputedAttribute import ComputedAttribute
from AccessControl import getSecurityManager
from Traversable import Traversable
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from DocumentTemplate.ustr import ustr
from zExceptions.ExceptionFormatter import format_exception
import time
from zLOG import LOG, BLATHER

import marshal
import ZDOM

HTML=Globals.HTML
StringType=type('')

class Item(Base, Resource, CopySource, App.Management.Tabs, Traversable,
           ZDOM.Element,
           AccessControl.Owned.Owned,
           App.Undo.UndoSupport,
           ):
    """A common base class for simple, non-container objects."""
    isPrincipiaFolderish=0
    isTopLevelPrincipiaApplicationObject=0
    
    def manage_afterAdd(self, item, container): pass
    def manage_beforeDelete(self, item, container): pass
    def manage_afterClone(self, item): pass

    # Direct use of the 'id' attribute is deprecated - use getId()
    id=''

    getId__roles__=None
    def getId(self):
        """Return the id of the object as a string. This method
           should be used in preference to accessing an id attribute
           of an object directly. The getId method is public."""
        name=getattr(self, 'id', None)
        if callable(name):
            return name()
        if name is not None:
            return name
        if hasattr(self, '__name__'):
            return self.__name__
        raise AttributeError, 'This object has no id'

    # Alias id to __name__, which will make tracebacks a good bit nicer:
    __name__=ComputedAttribute(lambda self: self.getId())

    # Name, relative to SOFTWARE_URL of icon used to display item
    # in folder listings.
    icon=''

    # Meta type used for selecting all objects of a given type.
    meta_type='simple item'

    # Default title.  
    title=''

    # Default propertysheet info:
    __propsets__=()
 
    manage_options=(
        App.Undo.UndoSupport.manage_options
        +AccessControl.Owned.Owned.manage_options
        )
    
    # Attributes that must be acquired
    REQUEST=Acquisition.Acquired

    # Allow (reluctantly) access to unprotected attributes
    __allow_access_to_unprotected_subobjects__=1


    def title_or_id(self):
        """
        Utility that returns the title if it is not blank and the id
        otherwise.
        """
        title=self.title
        if callable(title):
            title=title()
        if title: return title
        return self.getId()

    def title_and_id(self):
        """
        Utility that returns the title if it is not blank and the id
        otherwise.  If the title is not blank, then the id is included
        in parens.
        """
        title=self.title
        if callable(title):
            title=title()
        id = self.getId()
        return title and ("%s (%s)" % (title,id)) or id
    
    def this(self):
        # Handy way to talk to ourselves in document templates.
        return self

    def tpURL(self):
        # My URL as used by tree tag
        return self.getId()

    def tpValues(self):
        # My sub-objects as used by the tree tag
        return ()

    _manage_editedDialog=Globals.DTMLFile('dtml/editedDialog', globals())
    def manage_editedDialog(self, REQUEST, **args):
        return apply(self._manage_editedDialog,(self, REQUEST), args)

    def raise_standardErrorMessage(
        self, client=None, REQUEST={},
        error_type=None, error_value=None, tb=None,
        error_tb=None, error_message='',
        tagSearch=re.compile(r'[a-zA-Z]>').search):

        try:
            if error_type  is None: error_type =sys.exc_info()[0]
            if error_value is None: error_value=sys.exc_info()[1]
            
            # allow for a few different traceback options
            if tb is None and error_tb is None:
                tb=sys.exc_info()[2]
            if type(tb) is not type('') and (error_tb is None):
                error_tb = pretty_tb(error_type, error_value, tb)
            elif type(tb) is type('') and not error_tb:
                error_tb = tb

            try:
                log = aq_acquire(self, '__error_log__', containment=1)
            except AttributeError:
                pass
            else:
                log.raising((error_type, error_value, tb))

            # turn error_type into a string
            if hasattr(error_type, '__name__'):
                error_type=error_type.__name__

            if hasattr(self, '_v_eek'):
                # Stop if there is recursion.
                raise error_type, error_value, tb
            self._v_eek=1
   
            if str(error_type).lower() in ('redirect',):
                raise error_type, error_value, tb

            if not error_message:
                try:
                    s = ustr(error_value)
                except:
                    s = error_value
                try:
                    match = tagSearch(s)
                except TypeError:
                    match = None
                if match is not None:
                    error_message=error_value

            if client is None: client=self
            if not REQUEST: REQUEST=self.aq_acquire('REQUEST')

            try:
                if hasattr(client, 'standard_error_message'):
                    s=getattr(client, 'standard_error_message')
                else:
                    client = client.aq_parent
                    s=getattr(client, 'standard_error_message')
                kwargs = {'error_type': error_type,
                          'error_value': error_value,
                          'error_tb': error_tb,
                          'error_traceback': error_tb,
                          'error_message': error_message}

                if isinstance(s, HTML):
                    v = s(client, REQUEST, **kwargs)
                elif callable(s):
                    v = s(**kwargs)
                else:
                    v = HTML.__call__(s, client, REQUEST, **kwargs)
            except:
                LOG('OFS', BLATHER,
                    'Exception while rendering an error message',
                    error=sys.exc_info())
                try:
                    strv = str(error_value)
                except:
                    strv = '<unprintable %s object>' % str(type(error_value).__name__)
                v = strv + (
                    " (Also, an error occurred while attempting "
                    "to render the standard error message.)")
            raise error_type, v, tb
        finally:
            if hasattr(self, '_v_eek'): del self._v_eek
            tb=None

    def manage(self, URL1):
        " "
        raise 'Redirect', "%s/manage_main" % URL1 

    # This keeps simple items from acquiring their parents
    # objectValues, etc., when used in simple tree tags.
    def objectValues(self, spec=None):
        return ()
    objectIds=objectItems=objectValues

    # FTP support methods
    
    def manage_FTPstat(self,REQUEST):
        "psuedo stat, used by FTP for directory listings"
        from AccessControl.User import nobody
        mode=0100000
        
        # check read permissions
        if (hasattr(aq_base(self),'manage_FTPget') and 
            hasattr(self.manage_FTPget, '__roles__')):
            try:
                if getSecurityManager().validateValue(self.manage_FTPget):
                    mode=mode | 0440
            except: pass
            if nobody.allowed(self.manage_FTPget,
                              self.manage_FTPget.__roles__):
                mode=mode | 0004
                
        # check write permissions
        if hasattr(aq_base(self),'PUT') and hasattr(self.PUT, '__roles__'):
            try:
                if getSecurityManager().validateValue(self.PUT):
                    mode=mode | 0220
            except: pass
            
            if nobody.allowed(self.PUT, self.PUT.__roles__):
                mode=mode | 0002
                
        # get size
        if hasattr(aq_base(self), 'get_size'):
            size=self.get_size()
        elif hasattr(aq_base(self),'manage_FTPget'):
            size=len(self.manage_FTPget())
        else:
            size=0
        # get modification time
        if hasattr(aq_base(self), 'bobobase_modification_time'):
            mtime=self.bobobase_modification_time().timeTime()
        else:
            mtime=time.time()
        # get owner and group
        owner=group='Zope'
        if hasattr(aq_base(self), 'get_local_roles'):
            for user, roles in self.get_local_roles():
                if 'Owner' in roles:
                    owner=user
                    break
        return marshal.dumps((mode,0,0,1,owner,group,size,mtime,mtime,mtime))

    def manage_FTPlist(self,REQUEST):
        """Directory listing for FTP. In the case of non-Foldoid objects,
        the listing should contain one object, the object itself."""
        # check to see if we are being acquiring or not
        ob=self
        while 1:
            if App.Common.is_acquired(ob):
                raise ValueError('FTP List not supported on acquired objects')
            if not hasattr(ob,'aq_parent'):
                break
            ob=ob.aq_parent
            
        stat=marshal.loads(self.manage_FTPstat(REQUEST))
        id = self.getId()
        return marshal.dumps((id,stat))

    def __len__(self):
        return 1


Globals.default__class_init__(Item)

class Item_w__name__(Item):
    """Mixin class to support common name/id functions"""

    def title_or_id(self):
        """Utility that returns the title if it is not blank and the id
        otherwise."""
        return self.title or self.__name__

    def title_and_id(self):
        """Utility that returns the title if it is not blank and the id
        otherwise.  If the title is not blank, then the id is included
        in parens."""
        t=self.title
        return t and ("%s (%s)" % (t,self.__name__)) or self.__name__

    def _setId(self, id):
        self.__name__=id

    def getPhysicalPath(self):
        '''Returns a path (an immutable sequence of strings)
        that can be used to access this object again
        later, for example in a copy/paste operation.  getPhysicalRoot()
        and getPhysicalPath() are designed to operate together.
        '''
        path = (self.__name__,)
        
        p = aq_parent(aq_inner(self))
        if p is not None: 
            path = p.getPhysicalPath() + path
            
        return path


def pretty_tb(t, v, tb, as_html=1):
    tb = format_exception(t, v, tb, as_html=as_html)
    tb = '\n'.join(tb)
    return tb


class SimpleItem(Item, Globals.Persistent,
                 Acquisition.Implicit,
                 AccessControl.Role.RoleManager,
                 ):
    # Blue-plate special, Zope Masala
    """Mix-in class combining the most common set of basic mix-ins
    """

    manage_options=Item.manage_options+(
        {'label':'Security',
         'action':'manage_access',
         'help':('OFSP', 'Security.stx')},
        )
 
    __ac_permissions__=(('View', ()),)

    def __repr__(self):
        """Show the physical path of the object and its context if available.
        """
        try:
            path = '/'.join(self.getPhysicalPath())
        except:
            path = None
        context_path = None
        context = aq_parent(self)
        container = aq_parent(aq_inner(self))
        if aq_base(context) is not aq_base(container):
            try:
                context_path = '/'.join(context.getPhysicalPath())
            except:
                context_path = None
        res = '<%s' % self.__class__.__name__
        if path:
            res += ' at %s' % path
        else:
            res += ' at 0x%x' % id(self)
        if context_path:
            res += ' used for %s' % context_path
        res += '>'
        return res

