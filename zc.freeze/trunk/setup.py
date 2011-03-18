from setuptools import setup, find_packages

setup(
    name="zc.freeze",
    version="1.1b",
    install_requires=[
        'zc.copy >= 1.1b',
        'rwproperty',
        'setuptools',
        'zope.component',
        'zope.interface',
        'pytz',
        'ZODB3',
        'zope.event',
        'zope.annotation',
        'zope.cachedescriptors',
        'zope.locking >= 1.1b', # optional, actually
        'zope.testing',
        'zope.app.testing', # lame, should remove
        'zope.app.container', # lame, should remove
        ],
    packages=find_packages('src'),
    include_package_data=True,
    package_dir= {'':'src'},

    namespace_packages=['zc'],

    zip_safe=False,
    author='Zope Project',
    author_email='zope-dev@zope.org',
    url='http://pypi.python.org/pypi/zc.freeze',
    description=open('README.txt').read(),
    long_description=
        open('CHANGES.txt').read() +
        '\n\n' +
        open("src/zc/freeze/README.txt").read(),
    license='ZPL 2.1',
    keywords="zope zope3",
    )
