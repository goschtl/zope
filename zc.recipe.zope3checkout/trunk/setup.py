from setuptools import setup, find_packages

name = "zc.recipe.zope3checkout"

setup(
    name = name,
    version = "1.0",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "ZC Buildout recipe for installing a Zope 3 checkout",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "zope3 buildout",
    url='http://svn.zope.org/'+name,
    classifiers = [
        'Framework :: Buildout',
        'License :: OSI Approved :: Zope Public License',
        ],

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc', 'zc.recipe'],
    install_requires = ['zc.buildout', 'setuptools'],
    dependency_links = ['http://download.zope.org/distribution/'],
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
