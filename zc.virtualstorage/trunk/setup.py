from setuptools import setup, find_packages

setup(
    name="zc.virtualstorage",
    version="0.1",
    packages=find_packages('src'),
    include_package_data=True,
    package_dir= {'':'src'},
    
    namespace_packages=['zc'],

    zip_safe=False,
    author='Zope Project',
    author_email='zope-dev@zope.org',
    description=open("README.txt").read(),
    long_description=(
        open('src/zc/virtualstorage/CHANGES.txt').read() +
        '\n========\nOverview\n========\n\n' +
        open("src/zc/virtualstorage/README.txt").read()),
    license='ZPL 2.1',
    keywords="zope zope3",
    install_requires=[
        'ZODB3 >= 3.9dev',
        'zope.interface',
        'setuptools',
        
        'zope.testing',
        ],
    )
