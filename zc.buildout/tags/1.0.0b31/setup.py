import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'zc', 'buildout', 'buildout.txt')
        + '\n' +
        read('src', 'zc', 'buildout', 'repeatable.txt')
        + '\n' +
        read('src', 'zc', 'buildout', 'downloadcache.txt')
        + '\n' +
        read('src', 'zc', 'buildout', 'setup.txt')
        + '\n' +
        read('src', 'zc', 'buildout', 'update.txt')
        + '\n' +
        read('src', 'zc', 'buildout', 'debugging.txt')
        + '\n' +
        read('src', 'zc', 'buildout', 'testing.txt')
        + '\n' +
        read('src', 'zc', 'buildout', 'easy_install.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        )

open('doc.txt', 'w').write(long_description)

name = "zc.buildout"
setup(
    name = name,
    version = "1.0.0b31",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "System for managing development buildouts",
    long_description=long_description,
    license = "ZPL 2.1",
    keywords = "development build",
    url='http://www.python.org/pypi/zc.buildout',

    data_files = [('.', ['README.txt'])],
    packages = ['zc', 'zc.buildout'],
    package_dir = {'': 'src'},
    namespace_packages = ['zc'],
    install_requires = 'setuptools',
    include_package_data = True,
    tests_require = ['zope.testing'],
    test_suite = name+'.tests.test_suite',
    entry_points = {'console_scripts':
                    ['buildout = %s.buildout:main' % name]}, 
    zip_safe=False,
    classifiers = [
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Build Tools',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
    )
