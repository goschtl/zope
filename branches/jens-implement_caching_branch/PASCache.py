##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Classes: PASCacheable, PASRAMCacheManager

$Id$
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Cache import Cacheable
from AccessControl.Permissions import manage_users
from Products.StandardCacheManagers.RAMCacheManager import RAMCacheManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class PASCacheable(Cacheable):

    security = ClassSecurityInfo()


InitializeClass(PASCacheable)


manage_addPASRAMCacheManagerForm = PageTemplateFile(
    'www/prcmAdd', globals(), __name__='manage_addPASRAMCacheManagerForm')

def addPASRAMCacheManager( dispatcher
                         , id
                         , REQUEST=None
                         ):
    """ Add a new PASRAMCacheManager to the PluggableAuthService """
    cache = PASRAMCacheManager(id)
    dispatcher._setObject(cache.getId(), cache)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'PASRAMCacheManager+added.'
                                    % dispatcher.absolute_url() )

class PASRAMCacheManager(RAMCacheManager):

    meta_type = 'PAS RAM Cache Manager'

    security = ClassSecurityInfo()

    manage_stats = PageTemplateFile('www/prcmStats', globals())

    security.declareProtected(manage_users, 'manage_invalidate')
    def manage_invalidate(self, path, REQUEST=None):
        """ ZMI helper to invalidate an entry """
        try:
            ob = self.unrestrictedTraverse(path)
        except (AttributeError, KeyError):
            print 'Cannot delete', path

        ob.ZCacheable_invalidate()

        if REQUEST is not None:
            msg = 'Cache entry for %s invalidated' % path
            return self.manage_stats(manage_tabs_message=msg)


InitializeClass(PASRAMCacheManager)

