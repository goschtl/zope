from setuptools import setup, find_packages

setup(
    name = "z3c.i18n",
    version = "0.1",
    author = "Zope Contributors",
    author_email = "zope3-dev@zope.org",
    description = "I18n utils for zope3",
    license = "ZPL 2.1",
    keywords = "zope3 i18n",
    url='http://svn.zope.org/z3c.i18n',
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
        'zope.component',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        ],
    extras_require = {
        'test': ['zope.testing', 'zope.app.testing'],
        },
    dependency_links = ['http://download.zope.org/distribution/'],
    )
