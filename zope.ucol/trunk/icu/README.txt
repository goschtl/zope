Recipe for installing ICU into a buildout
=========================================

The zc.recipe.icu recipe installs the International Component for
Unicode (ICU) library into a `buildout
<http://www.python.org/pypi/zc.buildout>`_.

The recipe takes either a URL or a version. To download from the IBM
site, use a version, and the URL will be computed for you::

   [icu]
   recipe = zc.recipe.icu
   version = 3.2

Or you can specify a URL, for example to point to a cached copy.
