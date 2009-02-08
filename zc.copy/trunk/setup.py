from setuptools import setup, find_packages

setup(
    name="zc.copy",
    version="1.1",
    install_requires=[
        'setuptools',
        'ZODB3',
        'zope.component',
        'zope.interface',
        'zope.event',
        'zope.lifecycleevent',
        'zope.copypastemove',
        'zope.app.container',
        'zope.location',
        'zope.testing',
        ],
    packages=find_packages('src'),
    include_package_data=True,
    package_dir= {'':'src'},
    
    namespace_packages=['zc'],

    zip_safe=False,
    author='Zope Project',
    author_email='zope-dev@zope.org',
    description=open("README.txt").read(),
    long_description=
        open("src/zc/copy/CHANGES.txt").read() + '\n\n' +
        open("src/zc/copy/README.txt").read(),
    license='ZPL 2.1',
    keywords="zope zope3",
    )
