hurry.yui
=========

Introduction
------------

This library packages YUI for ``hurry.resource``. It is aware of YUI's
dependency structure and different modes (normal, minified and debug)
and consolidations.

Let's set up a way to render URLs; typically the framework has already
done this::

  >>> def get_inclusion_url(inclusion):
  ...    return 'http://localhost/static/%s/%s' % (
  ...      inclusion.library.name, inclusion.relpath)
  >>> from hurry.resource.interfaces import IInclusionUrl
  >>> from zope import component
  >>> component.provideUtility(get_inclusion_url, 
  ...     IInclusionUrl)


Let's check the YUI structure by picking out a resource in it::

  >>> from hurry import yui
  >>> from hurry.resource import NeededInclusions
  >>> needed = NeededInclusions()
  >>> needed.need(yui.fonts)
  >>> print needed.render()
  <link rel="stylesheet" type="text/css" href="http://localhost/static/yui/fonts/fonts.css" />

Let's try a resource that has a dependency on fonts, namely
``grids``::

  >>> needed = NeededInclusions()
  >>> needed.need(yui.grids)
  >>> print needed.render()
  <link rel="stylesheet" type="text/css" href="http://localhost/static/yui/fonts/fonts.css" />
  <link rel="stylesheet" type="text/css" href="http://localhost/static/yui/grids/grids.css" />

Now let's try to see consolidation: we include grids and reset at the
same time, and we expect a consolidation to ``reset-fonts-grids``::

  >>> needed = NeededInclusions()
  >>> needed.need(yui.grids)
  >>> needed.need(yui.reset)
  >>> print needed.render()
  <link rel="stylesheet" type="text/css" href="http://localhost/static/yui/reset-fonts-grids/reset-fonts-grids.css" />

Let's get the same, minified::

  >>> print needed.render(mode="minified")
  <link rel="stylesheet" type="text/css" href="http://localhost/static/yui/reset-fonts-grids/reset-fonts-grids-min.css" />

