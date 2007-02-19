====================
viewcache statistics
====================

viewcache statistics are based on the statistics you know from ramcache
but offer additional functionality to

* `invalidate cache entries`_
* show the different keys
* display their min and max lifetime XXX
* and show their dependencies XXX





The CacheView has been registered in the tests setUp method.
We can access the statistic view using the sitemanager

  >>> from zope.testbrowser.testing import Browser
  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> manager.handleErrors = False
  >>> manager.open('http://localhost:8080/++etc++site/default/view-cache-RAM/statistics.html')


Now we just add some fake rendered views to our cache. The cache entries are similar to the viewlets
used in the demo-package. we create a cache-entry for the idlist-viewlet with the key 'asc' and one 
with the key 'desc'. We create another cache-entry for the metadata-viewlet where we don't specify a key.
Both viewlet have a dependency on IFolder.

  >>> viewCache = root.getSiteManager()['default']['view-cache-RAM']
  >>> viewCache
  <lovely.viewcache.ram.ViewCache object at ...>
  
  >>> from zope.app.folder.interfaces import IFolder
  >>> viewCache.set('<div>some html snippets</div>', 'idlist', key={'key': u'asc'}, dependencies=[IFolder,])
  >>> viewCache.set('<div>some html snippets</div>', 'idlist', key={'key': u'desc'}, dependencies=[IFolder,])
  >>> viewCache.set('<div>some html snippets</div>', 'idlist', key={'key': u'desc'}, dependencies=[IFolder,])
  >>> viewCache.set('<div>some html</div>', 'metadatalist', key={'key': None}, dependencies=[IFolder,])


invalidate cache entries
========================

We want to display the cache-statistics now, and then select the entry with the key 'asc' for invalidation.

  >>> manager.open('http://localhost:8080/++etc++site/default/view-cache-RAM/statistics.html')
  >>> form = manager.getForm(index=0)
  >>> controls = form.getControl(name='ids:list')
  >>> items = controls.mech_control.get_items()
  >>> items[1].selected = True
  >>> from pprint import pprint as pp
  >>> pp([(input.id, input.selected) for input in items])
  [('idlist-None', False),
   ("idlist-(('key', u'asc'),)", True),
   ("idlist-(('key', u'desc'),)", False),
   ('metadatalist-None', False),
   ("metadatalist-(('key', None),)", False),
   ...
   
We see, that the checkbox of the 2nd entry has been selected. We click 'Invalidate' to remove this entry
from our cache
 
 >>> form.getControl(name='form.Invalidate').click()
 
As we open the statistics page again the respective cache-entry should be gone now:
  
  >> manager.open('http://localhost:8080/++etc++site/default/view-cache-RAM/statistics.html')
  >>> form = manager.getForm(index=0)
  >>> controls = form.getControl(name='ids:list')
  >>> items = controls.mech_control.get_items()
  >>> pp([(input.id, input.selected) for input in items])
  [('idlist-None', False),
   ("idlist-(('key', u'desc'),)", False),
   ('metadatalist-None', False),
   ("metadatalist-(('key', None),)", False),
   ...
   
   

The first row of a new view does not stand for a cache entry but for
all cache entries of the respective view.  It summarizes the sizes and
shows the number of cache-entries and the lifetime settings.

You can invalidate all cache entries for a view by invalidating this first row.

  >>> controls.controls[0].selected = True
  >>> form.getControl(name='form.Invalidate').click()

now all cache entries for the view `idlist` got removed from our cache.

  >>> manager.open('http://localhost:8080/++etc++site/default/view-cache-RAM/statistics.html')
  >>> form = manager.getForm(index=0)
  >>> controls = form.getControl(name='ids:list')
  >>> items = controls.mech_control.get_items()
  >>> pp([(input.id, input.selected) for input in items])
  [('metadatalist-None', False),
   ("metadatalist-(('key', None),)", False),
   ...

   
XXX show/test invalidateAll
