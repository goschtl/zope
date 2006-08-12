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
  >>> browser.getControl(name='lovely.sampledata.site.sitename').value = 'tags'
  >>> browser.getControl('Generate').click()

Tag cloud
---------

Shows a tag cloud.

  >>> browser.open('http://localhost/tags/@@tagCloud')
  >>> print browser.contents
  <div class="tagCloud">
   <span class="tag1">1970s(1)</span>
   ...
  </div>


Related tag cloud
-----------------

Shows a tag cloud of all related tags of a tag.

  >>> browser.open('http://localhost/tags/@@relatedTagCloud?tagname=1970s')
  >>> print browser.contents
  <div class="tagCloud">
   <span class="tag1">city(1)</span>
   ...
  </div>

