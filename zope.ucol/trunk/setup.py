from distutils.core import setup, Extension

setup(name='zope.ucol',
      version='1.0',
      ext_modules=[
          Extension('zope.ucol._zope_ucol',
                    ['src/zope/ucol/_zope_ucol.c'],
                    libraries=['icui18n', 'icuuc', 'icudata'],
           )
          ],
      packages=["zope", "zope.ucol"],
      package_dir = {'': 'src'},
      )
