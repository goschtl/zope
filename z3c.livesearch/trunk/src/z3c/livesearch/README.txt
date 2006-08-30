==========
Livesearch
==========

The z3c.livesearch package provides views which provide a Ajax based
livesearch field based on scriptacuolous.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

At first we need a site with a catalog and and intid util, we get this
from the z3c.sampledata package.

  >>> browser.open('http://localhost/@@managesamples.html')
  >>> browser.getLink('Site with Catalog').click()
  >>> browser.getControl('Sitename').value=u'livesearchsite'
  >>> browser.getControl('Generate').click()

Let us add the needed index

  >>> browser.open('http://localhost/livesearchsite/++etc++site/default/Catalog/+/AddTextIndex=')
  >>> browser.getControl(name='field.interface').value=[
  ...    'zope.index.text.interfaces.ISearchableText']
  >>> browser.getControl('Field Name').value='getSearchableText'
  >>> browser.getControl('Field Callable').selected=True
  >>> browser.getControl(name='add_input_name').value='getSearchableText'
  >>> browser.getControl('Add').click()


We can now call our result page which is an empty unordered list.

  >>> base = 'http://localhost/livesearchsite'

  >>> browser.open(base + '/@@livesearch/@@results?query=a')
  >>> print browser.contents
  <ul class="autocomplete">
  </ul>

Let us add 2 zpt pages which is indexed by our catalog.

  >>> browser.open(base + '/+/zope.app.zptpage.ZPTPage=')
  >>> browser.getControl('Source').value="apple pear"
  >>> browser.getControl('Add').click()

  >>> browser.open(base + '/+/zope.app.zptpage.ZPTPage=')
  >>> browser.getControl('Source').value="pear cherry"
  >>> browser.getControl('Add').click()

  >>> browser.open(base + '/@@livesearch/@@results?query=app')

We should have one match now labeled with the name.

  >>> browser.getLink('ZPTPage').url
  'http://localhost/livesearchsite/ZPTPage'

  >>> not '>ZPTPage-2<' in browser.contents
  True

Let us test some another queries.

  >>> browser.open(base + '/@@livesearch/@@results?query=notthere')
  >>> print browser.contents
  <ul class="autocomplete">
  </ul>

  >>> browser.open(base + '/@@livesearch/@@results?query=pea')
  >>> browser.getLink('ZPTPage').url
  'http://localhost/livesearchsite/ZPTPage'
  >>> browser.getLink('ZPTPage-2').url
  'http://localhost/livesearchsite/ZPTPage-2'

  >>> browser.open(base + '/@@livesearch/@@results?query=che')
  >>> browser.getLink('ZPTPage-2').url
  'http://localhost/livesearchsite/ZPTPage-2'

  >>> not '>ZPTPage<' in browser.contents
  True
