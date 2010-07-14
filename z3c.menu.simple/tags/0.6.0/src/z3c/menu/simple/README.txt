===========
Simple Menu
===========

The ``z3c.menu.simple`` package provides a simple menu implementation which
allows you to implement simply menus based on content providers and viewlets.

Right now there are some ``SimpleMenuItem`` menu item implementations and
a tabbed menu with tab/tab-item and action/action-item located in this
package.

Let's see what this means.


ContextMenu
-----------

  >>> from zope.viewlet.interfaces import IViewlet
  >>> from zope.viewlet.interfaces import IViewletManager

Let's create a menu which means we define a viewlet manager interface:

  >>> class IMenu(IViewletManager):
  ...     """Menu viewlet manager."""

You can then create a viewlet manager using this interface now:

  >>> from zope.viewlet import manager
  >>> Menu = manager.ViewletManager('left', IMenu)

Now we have to define a context:

  >>> import zope.interface
  >>> from zope.app.container import contained
  >>> from zope.app.container.interfaces import IContained
  >>> class Content(contained.Contained):
  ...     zope.interface.implements(IContained)
  >>> root['content'] = Content()
  >>> content = root['content']

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from zope.publisher.interfaces.browser import IBrowserView
  >>> class View(contained.Contained):
  ...     zope.interface.implements(IBrowserView)
  ...     def __init__(self, context, request):
  ...         self.__parent__ = context
  ...         self.context = context
  ...         self.request = request
  >>> view = View(content, request)

  >>> menu = Menu(content, request, view)

So initially no menu get rendered:

  >>> menu.update()
  >>> menu.render()
  u''

But now we register a context menu item for the `IMenu`:

  >>> import zope.component
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer

  >>> from z3c.menu.simple.menu import ContextMenuItem
  >>> class MyLocalLink(ContextMenuItem):
  ...
  ...     __name__ = u'MyLocalLink'
  ...     urlEndings = 'myLocal.html'
  ...     viewURL = 'myLocal.html'

  >>> # Create a security checker for viewlets.
  >>> from zope.security.checker import NamesChecker, defineChecker
  >>> viewletChecker = NamesChecker(('update', 'render'))
  >>> defineChecker(MyLocalLink, viewletChecker)

  >>> zope.component.provideAdapter(
  ...     MyLocalLink,
  ...     (zope.interface.Interface, IDefaultBrowserLayer,
  ...     IBrowserView, IMenu),
  ...     IViewlet, name='MyLocalLink')

Now see what we get if the IMenu viewlet manager get used:

  >>> menu.update()
  >>> print menu.render()
  <a href="http://127.0.0.1/content/myLocal.html"
     class="inactive-menu-item">MyLocalLink</a>


GlobalMenu
----------

  >>> from z3c.menu.simple.menu import GlobalMenuItem
  >>> class MyGlobalLink(GlobalMenuItem):
  ...
  ...     __name__ = u'MyGlobalLink'
  ...     urlEndings = 'myGlobal.html'
  ...     viewURL = 'myGlobal.html'

  >>> defineChecker(MyGlobalLink, viewletChecker)

  >>> zope.component.provideAdapter(
  ...     MyGlobalLink,
  ...     (zope.interface.Interface, IDefaultBrowserLayer,
  ...     IBrowserView, IMenu),
  ...     IViewlet, name='MyGlobalLink')

Now see what we get if the IMenu viewlet manager get used:

  >>> menu.update()
  >>> print menu.render()
  <a href="http://127.0.0.1/myGlobal.html"
     class="inactive-menu-item">MyGlobalLink</a>
  <a href="http://127.0.0.1/content/myLocal.html"
     class="inactive-menu-item">MyLocalLink</a>


TabbedMenu
----------

Now we create a tabbed menu called MasterMenu:

  >>> class IMasterMenu(IViewletManager):
  ...     """Master menu viewlet manager."""

Let's create a viewlet manager using this interface and the TabMenu as base
class:

  >>> from z3c.menu.simple.menu import TabMenu
  >>> MasterMenu = manager.ViewletManager('masterMenu', IMasterMenu,
  ...                                     bases=(TabMenu,))

We use the same context, request and view like before:

  >>> masterMenu = MasterMenu(content, request, view)

So initially no menu get rendered:

  >>> masterMenu.update()
  >>> masterMenu.render()
  u''

Now we register a menu tab which is also a viewlet manager:

  >>> from zope.browserpage import viewpagetemplatefile
  >>> from z3c.menu.simple import ITab
  >>> from z3c.menu.simple.menu import Tab
  >>> class MyTabs(Tab):
  ...     template = viewpagetemplatefile.ViewPageTemplateFile('tab.pt')
  >>> myTabs = MyTabs(content, request, view)

Also here, initially no tab get rendered:

  >>> myTabs.update()
  >>> myTabs.render()
  u''

Now we register a menu action which is also a viewlet manager:

  >>> from z3c.menu.simple import IAction
  >>> from z3c.menu.simple.menu import Action
  >>> class MyActions(Action):
  ...     template = viewpagetemplatefile.ViewPageTemplateFile('action.pt')
  >>> myActions = MyActions(content, request, view)

Also here, initially no tab get rendered:

  >>> myActions.update()
  >>> myActions.render()
  u''

After setup the `TabMenu`, `Tab` and `Action` viewlet managers, we start to
register a tab menu item:

  >>> from z3c.menu.simple.menu import TabItem
  >>> class MyTab(TabItem):
  ...
  ...     __name__ = u'MyTab'
  ...     url = 'myTab.html'
  ...     selectedViewNames = ['myTab.html']

  >>> tabChecker = NamesChecker(('update', 'render', 'css', 'selected'))
  >>> defineChecker(MyTab, tabChecker)

  >>> zope.component.provideAdapter(
  ...     MyTab,
  ...     (zope.interface.Interface, IDefaultBrowserLayer,
  ...     IBrowserView, ITab),
  ...     IViewlet, name='MyTab')

Now see what we get if the tab viewlet manager get rendered:

  >>> myTabs.update()
  >>> print myTabs.render()
  <div class="tabMenu">
    <span class="inactive-menu-item">
    <a href="myTab.html">MyTab</a>
  </span>
  </div>

After showing how a tab menu item get used, we will register a menu action
item.

  >>> from z3c.menu.simple.menu import ActionItem
  >>> class MyAction(ActionItem):
  ...
  ...     __name__ = u'MyAction'
  ...     title = 'myAction'

  >>> actionChecker = NamesChecker(('update', 'render', 'title'))
  >>> defineChecker(MyAction, actionChecker)

  >>> zope.component.provideAdapter(
  ...     MyAction,
  ...     (zope.interface.Interface, IDefaultBrowserLayer,
  ...     IBrowserView, IAction),
  ...     IViewlet, name='MyAction')

Now see what we get if the action viewlet manager get used:

  >>> myActions.update()
  >>> print myActions.render()
  <div class="actionMenuWrapper">
    <ul class="actionMenu">
      <li class="inactive-menu-item">
        <a href="">
          <div>myAction</div>
        </a>
      </li>
    </ul>
  </div>
  <div class="clearActionMenu" />
