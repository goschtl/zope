hurry.zopeyui
*************

If you want to use YUI in Grok or Zope, you add a dependency to this
package in your setup.py. You can then import from ``hury.yui`` and
``need`` the resources you want to use.

This is a very thin integration layer between Zope and
``hurry.yui``. Right now it only publishes the YUI code
(``yui-build``) in ``hurry.yui`` as a Zope 3 resource directory.
