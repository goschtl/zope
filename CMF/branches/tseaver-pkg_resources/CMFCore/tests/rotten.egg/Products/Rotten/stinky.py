""" Rotten content object.

$Id$
"""
from pkg_resources import resource_string

from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from Products.CMFCore.URLTool import URLTool

class Stinky(URLTool):
    """
    """
    security = ClassSecurityInfo()

    manage_tabs = ({'label' : 'Stench', 'action' : 'manage_stench'},
                  ) + URLTool.manage_options

    manage_stench = ZopePageTemplate('manage_stench',
                                     resource_string(__name__,
                                                     'zmi/stench.pt'),
                                    )

InitializeClass(Stinky)
