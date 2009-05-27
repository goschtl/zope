from setuptools import setup, find_packages
import os.path

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '3.7.1'


setup(name='zope.app.pagetemplate',
      version=version,
      url='http://pypi.python.org/pypi/zope.app.pagetemplate',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='PageTemplate integration for Zope 3',
      long_description=(
        read('README.txt')
        + '\n\n.. contents::\n\n' +
        read('src', 'zope', 'app', 'pagetemplate', 'tests', 'test_nested.txt')
        + '\n\n' +
        read('src', 'zope', 'app', 'pagetemplate', 'namedtemplate.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
      license='ZPL 2.1',
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
          'zope.pagetemplate>=3.5.0',
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
          "test": ['zope.container',
                   'zope.app.testing',
                   'zope.app.securitypolicy',
                   'zope.app.zcmlfiles',
                  ],
          },
      zip_safe=False,
      )
