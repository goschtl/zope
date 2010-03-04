import os
from setuptools import setup, find_packages

tests_require = [
    'zope.security',
    'zope.testbrowser',
    'zope.securitypolicy',
    'zope.app.testing',
    'zope.testing',
    'grokcore.component',
    ]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='grokui.base',
      version='0.2dev',
      description="The Grok administration and development UI (base)",
      long_description=(
        read('README.txt') +
        '\n\n' +
        read(os.path.join('src', 'grokui', 'base', 'README.txt')) +
        '\n\n' +
        read('CHANGES.txt')
        ),
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'], 
      keywords="zope3 grok grokadmin",
      author="Uli Fouquet and Souheil Chelfouh",
      author_email="grok-dev@zope.org",
      url="http://svn.zope.org/grokui.base",
      license="ZPL 2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      namespace_packages = ['grokui'],
      install_requires=[
          'grok',
          'megrok.layout',
          'megrok.menu',
          'grokcore.message',
          'zope.authentication',
          'zope.browsermenu',
          'zope.component',
          'zope.interface',
          'zope.location',
          'zope.publisher',
          'zope.site',
          'zope.traversing',
          'setuptools',
          ],
      tests_require = tests_require,
      extras_require = dict(test=tests_require),
      entry_points="""
      # Add entry points here
      """,
      )
