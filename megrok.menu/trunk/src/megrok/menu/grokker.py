import martian
import grokcore.component
import megrok.menu
from martian.error import GrokError
#from grok.meta import ViewGrokker, default_view_name
from grokcore.view.meta.views import ViewGrokker, default_view_name

from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IBrowserPage
from zope.app.publisher.browser.menumeta import menuDirective, menuItemDirective
from zope.app.security.protectclass import protectName

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

class MenuItemGrokker(ViewGrokker):
    martian.directive(megrok.menu.menuitem)
    martian.directive(grokcore.component.title, default=u'')
    martian.directive(grokcore.component.description, default=u'')

    def execute(self, factory, config, context, layer, name, permission,
                menuitem, title, description, **kw):
        if menuitem is None:
            return False
        menu_id, icon, filter, order = menuitem
        try:
            menu = config.resolve('zope.app.menus.'+menu_id)
        except ConfigurationError, v:
            raise GrokError("The %r menu could not be found.  Please use "
                            "megrok.menu.Menu to register a menu first."
                            % menu_id, factory)
        menuItemDirective(config, menu=menu, for_=context, action=name,
                          title=title, description=description, icon=icon,
                          filter=filter, permission=permission, layer=layer,
                          order=order)

        # Menu items check whether the view that they refer to can be
        # traversed to.  Unfortunately, views will end up being
        # security proxied during that fake traversal.  For this to
        # work then, we must define a checker not only for __call__
        # but also for browserDefault and those other methods from
        # IBrowserPage:
        if permission is None:
            permission = 'zope.Public'
        for method_name in list(IBrowserPage):
            if method_name == '__call__':
                continue
            config.action(
                discriminator=('protectName', factory, method_name),
                callable=protectName,
                args=(factory, method_name, permission),
                )

        return True
