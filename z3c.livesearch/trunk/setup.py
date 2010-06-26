from setuptools import setup, find_packages

setup(
    name = "z3c.livesearch",
    version = "0.1",
    author = "Zope Contributors",
    author_email = "zope3-dev@zope.org",
    description = "Livesearch for zope3",
    license = "ZPL 2.1",
    keywords = "zope3 search live ajax javascript",
    url='http://svn.zope.org/z3c.livesearch',
    classifiers = [
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: Zope Public License",
        "Framework :: Zope :: UI",
        ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    zip_safe=False,
    install_requires = [
        'setuptools',
        'zc.resourcelibrary',
        'zope.app.catalog',
        'zope.app.intid',
        'z3c.javascript',
        ],
    extras_require = {
        'test': [
            'z3c.sampledata',
            'zope.app.keyreference',
            'zope.app.testing',
            'zope.app.zcmlfiles',
            'zope.app.zptpage',
            ],
        }
    )
