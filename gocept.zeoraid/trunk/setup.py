from setuptools import setup, find_packages

name = "gocept.zeoraid"
setup(
    name = name,
    version = "dev",
    author = "Christian Theune",
    author_email = "ct@gocept.com",
    description = "A ZODB storage for replication using RAID techniques.",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "zodb buildout",
    classifiers = ["Framework :: Buildout"],
    url='http://launchpad.net/'+name,
    zip_safe=False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['gocept'],
    install_requires = ['setuptools', 'ZODB3<3.9dev'],
    extras_require = {
        'recipe': ['zc.buildout']
    },
    entry_points = {
        'zc.buildout': [
            'default = %s.recipe:Recipe [recipe]' % name,
        ]},
    )
