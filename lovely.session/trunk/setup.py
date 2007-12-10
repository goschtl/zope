import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('src', 'lovely', 'session', 'README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Download\n'
        '========\n'
        )

name='lovely.session'
setup(
    name = name,
    version = '0.1.2',
    author = "Lovely Systems GmbH",
    author_email = "office@lovelysystems.com",
    description = "memcache session",
    long_description = long_description,
    license = "ZPL 2.1",
    keywords = "session zope zope3",
    url = 'https://launchpad.net/lovely.tal',
    zip_safe = False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely',],
    install_requires = ['setuptools',
                        'lovely.memcached',
                        'zope.app.container',
                        'zope.app.session',
                        'zope.schema',
                        ],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.interface',
                'zope.security',
                'zope.testing',]),
    classifiers = [
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],        
    )

