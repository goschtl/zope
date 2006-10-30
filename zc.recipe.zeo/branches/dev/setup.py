from setuptools import setup, find_packages

name = "zc.recipe.zeo"
setup(
    name = name,
    version = "1.0.0a1",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "ZC Buildout recipe for working with ZEO",
    license = "ZPL 2.1",
    keywords = "zodb zeo buildout",
    url='http://www.python.org/pypi/'+name,

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc', 'zc.recipe'],
    install_requires = [
        'zc.buildout',
        'zc.recipe.egg',
        'setuptools',],
    entry_points = {'zc.buildout': ['default = %s:Instance' % name]},
    )
