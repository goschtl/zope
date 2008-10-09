hurry.yui
=========

Introduction
------------

This library packages tinymce for ``hurry.resource``. 

Let's set up a way to render URLs; typically the framework has already
done this::

  >>> def get_library_url(library):
  ...    return 'http://localhost/static/%s' % (
  ...      library.name)
  >>> from hurry.resource import Library
  >>> from hurry.resource.interfaces import ILibraryUrl
  >>> from zope import component
  >>> component.provideAdapter(
  ...     factory=get_library_url, 
  ...     adapts=(Library,),
  ...     provides=ILibraryUrl)

Let's now check whether we can need tinymce::

  >>> from hurry import tinymce
  >>> from hurry.resource import NeededInclusions
  >>> needed = NeededInclusions()
  >>> needed.need(tinymce.tinymce)
  >>> print needed.render()
  <script type="text/javascript" src="http://localhost/static/tinymce/tiny_mce_src.js"></script>

