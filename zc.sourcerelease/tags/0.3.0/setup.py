import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

entry_points = """
[console_scripts]
buildout-source-release = zc.sourcerelease:source_release
"""

long_description=(
    '.. contents::\n\n'
    +
    read('src', 'zc', 'sourcerelease', 'README.txt')
    + '\n' +
    read('src', 'zc', 'sourcerelease', 'CHANGES.txt')
    + '\n' +
    'Download\n'
    '========\n'
    )

setup(
    name = "zc.sourcerelease",
    description = "Utility script to create source releases from buildouts",
    version = "0.3.0",
    license = "ZPL 1.0",
    url='http://www.python.org/pypi/zc.sourcerelease',
    author='Jim Fulton', author_email='jim@zope.com',
    long_description=long_description,
    
    entry_points = entry_points,
    packages = find_packages('src'),
    include_package_data = True,
    zip_safe = False,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        ],
    )
