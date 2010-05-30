import os
from setuptools import setup, find_packages

tests_require = [
    'z3c.testsetup',
    'zope.app.testing',
    'zope.testbrowser',
    'zope.testing',
    'zope.securitypolicy'
    ]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='grokui.zodbbrowser',
      version='0.1dev',
      description="The Grok administration and development UIs ZODB browser",
      long_description=(
          read(os.path.join('src', 'grokui', 'zodbbrowser', 'README.txt')) +
          '\n\n' +
          read('CHANGES.txt')
        ),
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
      keywords="zope3 grok grokui zodb zodbbrowser",
      author="Uli Fouquet and lots of contributors from grok community",
      author_email="grok-dev@zope.org",
      url="http://svn.zope.org/grokui.zodbbrowser",
      license="ZPL 2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['grokui'],
      install_requires=[
          'ZODB3',
          'grok',
          'grokcore.component',
          'grokui.base',
          'megrok.layout >= 1.0.1',
          'setuptools',
          'zope.component',
          'zope.interface',
          'zope.location',
          'zope.proxy',
          'zope.schema',
          'zope.security',
          'zope.session',
          'zope.site',
          ],
      tests_require = tests_require,
      extras_require = dict(test=tests_require),
      entry_points="""
      # Add entry points here
      """,
      )
