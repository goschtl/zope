import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = "zc.recipe.icu"
setup(
    name = name,
    version = "1.0.0b1",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = ("ZC Buildout recipe for installing the ICU library"
                   " into a buildout"),
    long_description= read('README.txt'),
    license = "ZPL 2.1",
    keywords = "development build internationalization",
    url='http://www.python.org/pypi/'+name,

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc', 'zc.recipe'],
    install_requires = ['setuptools'],
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    classifiers = [
       'Framework :: Buildout',
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       ],
    )
