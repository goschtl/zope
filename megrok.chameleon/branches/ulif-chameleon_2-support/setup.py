import os
from setuptools import setup, find_packages

version = '1.0.0dev'

install_requires = [
    'setuptools',
    'grokcore.component',
    'grokcore.view',
    'Chameleon >= 2.0-rc1',
    'z3c.pt >= 2.0-rc1',
    ]

tests_require = [
    'grokcore.viewlet',
    'zope.app.wsgi',
    'zope.app.zcmlfiles',
    ]

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open(os.path.join('src', 'megrok', 'chameleon',
                                      'README.txt')).read() +
                    '\n\n' +
                    open('CHANGES.txt').read())

setup(name='megrok.chameleon',
      version=version,
      description="Chameleon page template support for Grok",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python :: 2.5',
                   'Operating System :: OS Independent',
                   'Topic :: Internet :: WWW/HTTP',
                   ],
      keywords="grok chameleon template",
      author="Uli Fouquet",
      author_email="grok-dev@zope.org",
      url="http://pypi.python.org/pypi/megrok.chameleon",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      )
