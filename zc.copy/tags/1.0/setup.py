from setuptools import setup, find_packages

setup(
    name="zc.copy",
    version="1.0",
    install_requires=[],
#    dependency_links=['http://download.zope.org/distribution/',],
    packages=find_packages('src'),
    include_package_data=True,
    package_dir= {'':'src'},
    
    namespace_packages=['zc'],

    zip_safe=False,
    author='Zope Project',
    author_email='zope3-dev@zope.org',
    description=open("src/zc/copy/README.txt").read(),
    license='ZPL 2.1',
    keywords="zope zope3",
    )
