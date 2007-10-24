from setuptools import setup, find_packages

entry_points = """
[console_scripts]
buildout-source-release = zc.sourcerelease:source_release
"""

setup(
    name = "zc.sourcerelease",
    description = "Utility script to create source releases from buildouts",
    version = "0.1",
    license = "ZPL 1.0",
    url='http://www.python.org/pypi/zc.sourcerelease',
    author='Jim Fulton', author_email='jim@zope.com',
    
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
