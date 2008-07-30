from setuptools import setup, find_packages

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())

setup(name='zope.app.pagetemplate',
      version = '3.4.1',
      url='http://pypi.python.org/pypi/zope.app.pagetemplate',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='PageTemplate integration for Zope 3',
      long_description=long_description,
      classifiers=['Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python',
                   'Framework :: Zope3',
                   ],

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
