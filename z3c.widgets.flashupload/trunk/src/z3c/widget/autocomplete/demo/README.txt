=======================
AutoCompleteWidget Demo
=======================

This demo packe provides a simple content class which uses the
z3c autocomplete widget.

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.open('http://localhost/@@contents.html')

It can be added by clicking on the "Autocomplete Widget Demo" link in the
add menu. And giving it a name.

    >>> link = browser.getLink('Autocomplete Widget Demo')
    >>> link.click()
    >>> nameCtrl = browser.getControl(name='new_value')
    >>> nameCtrl.value = 'mydemo'
    >>> applyCtrl = browser.getControl('Apply')
    >>> applyCtrl.click()
    >>> link = browser.getLink('mydemo')
    >>> link.click()
    >>> browser.url
    'http://localhost/mydemo/@@edit.html'

Let us test the widget rendering by direct access.

    >>> browser.open('http://localhost/mydemo/@@edit.html/++widget++country')
    >>> print browser.contents
    <input class="textType" ...
    </script>

The suggestions are proveded by its own view.    

    >>> browser.open('http://localhost/mydemo/@@edit.html/++widget++country/suggestions')
    >>> print browser.contents

    >>> browser.open('http://localhost/++lang++en/mydemo/@@edit.html/++widget++country/suggestions?value=a')
    >>> print browser.contents
    <BLANKLINE>
     <ul>
      <li>Algeria</li>
      <li>Andorra</li>
      <li>Antigua and Barbuda</li>
      <li>Afghanistan</li>
      <li>Anguilla</li>
      <li>Armenia</li>
      <li>Albania</li>
      <li>Angola</li>
      <li>Antarctica</li>
      <li>American Samoa</li>
      <li>Argentina</li>
      <li>Australia</li>
      <li>Austria</li>
      <li>Aruba</li>
      <li>Azerbaijan</li>
     </ul>
    <BLANKLINE>
    <BLANKLINE>

Suggestions are translated.

    >>> browser.open('http://localhost/++lang++de/mydemo/@@edit.html/++widget++country/suggestions?value=a')
    >>> print browser.contents
    <BLANKLINE>
     <ul>
      <li>Amerikanische Jungferninseln</li>
      <li>Amerikanisch-Ozeanien</li>
      <li>Algerien</li>
      <li>Andorra</li>
      <li>Antigua und Barbuda</li>
      <li>Afghanistan</li>
      <li>Anguilla</li>
      <li>Armenien</li>
      <li>Albanien</li>
      <li>Angola</li>
      <li>Antarktis</li>
      <li>Amerikanisch-Samoa</li>
      <li>Argentinien</li>
      <li>Australien</li>
      <li>Aruba</li>
      <li>Aserbaidschan</li>
     </ul>
    <BLANKLINE>
    <BLANKLINE>
