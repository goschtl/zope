import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('src', 'lovely', 'persistent', 'README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        )

name='lovely.persistent'
setup(
    name = name,
    version = '0.1.1',
    author = "Lovely Systems GmbH",
    author_email = "office@lovelysystems.com",
    description = "improved ZODB persistence",
    long_description = long_description,
    license = "ZPL 2.1",
    keywords = "persistent zope zope3",
    url = 'http://launchpad.net/lovely.persistent',
    zip_safe = False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely',],
    install_requires = ['setuptools',
                        'ZODB3',
                        ],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.testing',]),

    classifiers = [
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],    
    )

