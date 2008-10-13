hurry.zopetinymce
*****************

If you want to use TinyMCE in Grok or Zope, you add a dependency to this
package in your setup.py. You can then import from ``hury.tinymce`` and
``need`` the resources you want to use.

This is a very thin integration layer between Zope and
``hurry.tinymce``. Right now it only publishes the TinyMCE code
(``tinymce-build``) in ``hurry.tinymce`` as a Zope 3 resource directory.
