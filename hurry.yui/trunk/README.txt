Preparing hurry.yui before release
==================================

Follow the regular package release instructions, but before egg
generation (``python setup.py register sdist upload``) first execute
``bin/yuiprepare <version number>``, where version number is the
version of the YUI release, such as ``2.6.0``. This will do two
things:

* download the YUI of that version and place it in the egg

* download the YUI dependency structure of that YUI version and generate
  a ``yui.py`` file in the package that reflects this.

