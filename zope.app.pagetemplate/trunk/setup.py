from setuptools import setup, find_packages

setup(name='zope.app.pagetemplate',
      version = '3.4.0b1',
      url='http://svn.zope.org/zope.app.pagetemplate',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',

      packages=find_packages('src'),
      package_dir={'': 'src'},

      namespace_packages=['zope', 'zope.app'],
      include_package_data=True,
      install_requires=[
          'setuptools',
          'zope.component [hook]',
          'zope.configuration',
          'zope.dublincore',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.pagetemplate',
          'zope.publisher',
          'zope.schema',
          'zope.security [untrustedpython]',
          'zope.size',
          'zope.tales',
          'zope.traversing',
          ],
      extras_require={
          "inline-evaluation": ['zope.app.interpreter'],
          # The tests appear not to need zope.app.interpreter; there
          # should be tests for that, though.  :-(
          "test": ['zope.app.testing',
                   'zope.app.securitypolicy',
                   'zope.app.zcmlfiles'],
          },
      zip_safe=False,
      )
