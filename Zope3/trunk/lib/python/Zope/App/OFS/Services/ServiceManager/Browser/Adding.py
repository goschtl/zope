##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Adding components for components and configuration

$Id: Adding.py,v 1.2 2002/11/30 18:39:17 jim Exp $
"""

from Zope.App.OFS.Container.Views.Browser.Adding import Adding as ContentAdding


class ComponentAdding(ContentAdding):
    """Adding component for components
    """
    
    menu_id = "add_component"

    def action(self, type_name, id):
        if not id:
            # Generate an id from the type name
            id = type_name
            if id in self.context:
                i=2
                while ("%s-%s" % (id, i)) in self.context:
                    i=i+1
                id = "%s-%s" % (id, i)
        return super(ComponentAdding, self).action(type_name, id)

class ConfigurationAdding(ContentAdding):
    """Adding component for configuration
    """
    
    menu_id = "add_configuration"
