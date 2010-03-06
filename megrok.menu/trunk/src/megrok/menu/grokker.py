
# -*- coding: utf-8 -*-

import martian
import megrok.menu

import grokcore.view
import grokcore.viewlet
import grokcore.security
import grokcore.component

from grokcore.view.meta.views import ViewSecurityGrokker, default_view_name
from martian.error import GrokError
from zope.browsermenu.metaconfigure import (
    menuDirective, menuItemDirective, subMenuItemDirective)
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IBrowserPage
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class MenuGrokker(martian.ClassGrokker):
    martian.component(megrok.menu.Menu)
    martian.priority(1500)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.component.title, default=u'')
    martian.directive(grokcore.component.description, default=u'')

    def execute(self, factory, config, name, title, description, **kw):
        menuDirective(config, id=name, class_=factory,
                      title=title, description=description)
        return True


class SubMenuItemGrokker(martian.ClassGrokker):
    martian.component(megrok.menu.SubMenuItem)

    # We want to do this after MenuGrokker.
    martian.priority(1000)

    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.component.title, default=u'')
    martian.directive(grokcore.component.description, default=u'')
    martian.directive(grokcore.viewlet.order)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.security.require, name='permission')

    martian.directive(megrok.menu.menuitem)

    def execute(self, factory, config, name, title, description,
                order = None, menuitem=None, context=None,
                layer=None, permission=None):

        menuDirective(config, id=name, class_=factory,
                      title=title, description=description)
        
        if menuitem is None:
            return False

        menu_id, icon, filter, enforced_order, extra = menuitem
       
        if enforced_order is None:
            enforced_order = order[0] or 0

        try:
            menu = config.resolve('zope.app.menus.'+menu_id)
        except ConfigurationError, v:
            raise GrokError("The %r menu could not be found.  Please use "
                            "megrok.menu.Menu to register a menu first."
                            % menu_id, factory)

        subMenuItemDirective(
            config, menu=menu, for_=context, submenu=name,
            title=title, description=description, icon=icon,
            filter=filter, permission=permission, layer=layer,
            order=enforced_order, action='', extra=extra
            )
        return True


class MenuItemGrokker(ViewSecurityGrokker):
    martian.directive(megrok.menu.menuitem)
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.viewlet.order)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.component.title, default=u'')
    martian.directive(grokcore.component.description, default=u'')
    martian.directive(
        grokcore.view.require, default="zope.View", name='permission')

    def execute(self, factory, config, permission, order, context=None,
                layer=None, name=u'', menuitem=None, description=u'',
                title=u''):

        if menuitem is None:
            return False
        
        menu_id, icon, filter, enforced_order, extra = menuitem
        
        if enforced_order is None:
            enforced_order = order[0] or 0

        try:
            menu = config.resolve('zope.app.menus.'+menu_id)
        except ConfigurationError, v:
            raise GrokError("The %r menu could not be found.  Please use "
                            "megrok.menu.Menu to register a menu first."
                            % menu_id, factory)

        menuItemDirective(config, menu=menu, for_=context, action=name,
                          title=title, description=description, icon=icon,
                          filter=filter, permission=permission, layer=layer,
                          order=enforced_order, extra=extra)
        return True
