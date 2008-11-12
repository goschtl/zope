import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('src', 'lovely', 'tal', 'README.txt')
        )
#long_description=()

name='lovely.tal'
setup(
    name = name,
    version = '0.5.0a1',
    author = "Lovely Systems GmbH",
    author_email = "office@lovelysystems.com",
    description = "the lovely tal enables new tal expressions",
    long_description = long_description,
    license = "ZPL 2.1",
    keywords = "tal zope zope3",
    url = 'http://launchpad.net/lovely.tal',
    zip_safe = False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely',],
    install_requires = ['setuptools',
                        'zope.tales',
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

