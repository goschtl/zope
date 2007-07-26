from setuptools import setup, find_packages

name = "gocept.zope3instance"
setup(
    name = name,
    version = "2.0a2",
    author = "Christian Theune",
    author_email = "ct@gocept.com",
    description = "zc.buildout recipe for defining a Zope 3 instance",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "zope3 buildout",
    url='http://svn.zope.org/'+name,
    classifiers = ["Framework :: Buildout"],

    zip_safe=False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['gocept'],
    install_requires = [
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        'zope.app.preference',
        'zope.app.securitypolicy',
        'zope.app.server',
        'zope.app.tree',
        'zope.app.zcmlfiles',
    ],
    extras_require=dict(test=['zope.testing']),
    dependency_links = ['http://amy.gocept.com/~ctheune/eggs/'],
    entry_points = {
        'zc.buildout': [
             'default = %s:Recipe' % name,
             ]
        },
    )
