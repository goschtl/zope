##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Vocabulary for the search scope.

$Id: vocabulary.py 25177 2004-06-02 13:17:31Z rogerineichen $
"""
import ldapurl

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.app import zapi
from zope.app.renderer.interfaces import ISource



def SearchScopeVocabulary(context):
    """Provide a select field for to select the search scope.
       
    For to select the search scope the ldap package use the 
    following definition:
    
    LDAP_SCOPE_BASE = 0
    LDAP_SCOPE_ONELEVEL = 1
    LDAP_SCOPE_SUBTREE = 2
    
    SEARCH_SCOPE_STR = {None:'',0:'base',1:'one',2:'sub'}
    
    SEARCH_SCOPE = {
      '':None,
      # the search scope strings defined in RFC2255
      'base':LDAP_SCOPE_BASE,
      'one':LDAP_SCOPE_ONELEVEL,
      'sub':LDAP_SCOPE_SUBTREE,
    }
    
    """
    scopeDict = ldapurl.SEARCH_SCOPE_STR
    
    #SEARCH_SCOPE_STR = {None:'',0:'base',1:'one',2:'sub'}
    
    return SimpleVocabulary(
        [SimpleTerm(key, title=value) for key, value in 
         scopeDict.items()])
