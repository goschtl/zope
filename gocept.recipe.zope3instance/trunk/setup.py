from setuptools import setup, find_packages

name = "gocept.zope3instance"
setup(
    name = name,
    version = "1.0b1",
    author = "Christian Theune",
    author_email = "ct@gocept.com",
    description = "zc.buildout recipe for defining a Zope 3 instance",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "zope3 buildout",
    url='http://svn.zope.org/'+name,

    zip_safe=False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['gocept'],
    install_requires = ['zc.buildout', 'zope.testing', 'setuptools',
                        'zc.recipe.egg'],
    dependency_links = ['http://download.zope.org/distribution/'],
    entry_points = {
        'zc.buildout': [
             'default = %s:Recipe' % name,
             ]
        },
    )
