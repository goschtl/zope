=============
Tagging Views
=============

We provide default views which are relevant for tagging.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization','Basic mgr:mgrpw')
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/@@managesamples.html')
  >>> browser.getLink(text='tagbrowsertest').click()
  >>> browser.getControl(name='z3c.sampledata.site.sitename').value = 'tags'
  >>> browser.getControl('Generate').click()

Tag cloud
---------

Shows a tag cloud.

  >>> browser.open('http://localhost/tags/@@tagCloud')
  >>> print browser.contents
  <div class="tagCloud">
   <span class="tag1">adam(1)</span>
   ...
  </div>


Related tag cloud
-----------------

Shows a tag cloud of all related tags of a tag.

  >>> browser.open('http://localhost/tags/@@relatedTagCloud?tagname=adam')
  >>> print browser.contents
  <div class="tagCloud">
   <span class="tag1">mysteries(1)</span>
  </div>


Engine specific Views
---------------------

CSV export of tag database:

  >>> engine = 'http://localhost/tags/++etc++site/default/tagging-engine/'
  >>> browser.open(engine + '@@tags.csv')
  >>> print browser.contents
  Name,User,Item,Timestamp
  ...

Normalize Tags:

  >>> browser.open(engine + 'manage.html')
  >>> browser.getControl(u'Normalize').click()
  >>> u'No normalizer function defined' in browser.contents
  True

All tags are lowercase so it should not affect any tags.

  >>> browser.getControl(u'Normalizer').value="string.lower"
  >>> browser.getControl(u'Normalize').click()
  >>> print browser.contents
  <...<div class="summary">Normalized 0 tag objects</div>...

Let us convert it to upper case.

  >>> browser.getControl(u'Normalizer').value="string.upper"
  >>> browser.getControl(u'Normalize').click()
  >>> print browser.contents
  <...<div class="summary">Normalized 111 tag objects</div>...

  >>> browser.open('http://localhost/tags/@@tagCloud')
  >>> print browser.contents
  <div class="tagCloud">
   <span class="tag1">ADAM(1)</span>
   <span class="tag6">ALEX(2)</span>
   <span class="tag1">ALTERNATIVE(1)</span>
   <span class="tag1">AMSTERDAM(1)</span>
   <span class="tag1">ANIMALS(1)</span>
  ...

Renaming Tags:

  >>> browser.open(engine + 'manage.html')
  >>> browser.getControl(u'Rename Tag').click()
  >>> u'Please define old and new name.' in browser.contents
  True
  >>> browser.getControl(u'Old Name').value = u'ADAM'
  >>> browser.getControl(u'New Name').value = u'NOTREDAM'
  >>> browser.getControl(u'Rename Tag').click()
  >>> print browser.contents
  <...<div class="summary">Renamed 1 tag objects</div>...

Cleaning of stale items:

  >>> browser.open(engine + 'manage.html')
  >>> browser.getControl(u'Clean Stale Items').click()
  >>> print browser.contents
  <...<div class="summary">Cleaned out 1 items</div>...
