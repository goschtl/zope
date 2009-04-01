===================
megrok.ootbviewlets
===================

This package has some ready2use Viewlets and ViewletManagers
for common parts of WebSites. megrok.ootbviewlets takes 
z3c.menu.simple [1] as base. So if you want to see more in
detail description. Please take a look in the documentation
and tests of z3c.menu.simple.

An example say´s more than 1000 words...
----------------------------------------

class MyManager(TabMenu):
    grok.name('mymanager')

class MyTab(TabItem):
    grok.name('delete')

    urlEndings = ['delete', ]
    viewURL = 'delete'

If you render the MyManager you will get this output:

  <div class="tabMenu">
    <span class="inactive-menu-item">
    <a href="http://localhost/tabs/delete">delete</a>
  </span>
  </div> 


So what are common parts in a WebSite:
--------------------------------------

- ContextMenuItems
  This Viewlet is useful if you need to create an send_to link
  on every object. You can use a grok.ViewletManager for ContextMenuItems.

- GlobalMenuItems
  This Viewlet allows you add global Items to your site.
  For example a logout link. You can use a grok.ViewletManager
  for GlobalMenuItems

- TabItemMenu, TabItem
  TabItemMenu is a ViewletManager which renders TabItems in this form:

- ActionItemMenu, ActionItem
  The ViewletManager ActionItemMenu renders the ActionItems which are Viewlets
  
  

[1] http://pypi.python.org/z3c.menu.simple
