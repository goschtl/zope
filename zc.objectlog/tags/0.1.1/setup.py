import os
from setuptools import setup, find_packages

long_description = (open("README.txt").read() +
                    '\n\n' +
                    open(os.path.join("src","zc","objectlog","log.txt")).read())

setup(
    name="zc.objectlog",
    version="0.1.1",
    license="ZPL 2.1",
    author="Zope Corporation",
    author_email="zope-dev@zope.org",
    description='Customizable object log for Zope3',
    long_description=long_description,
    keywords="zope zope3 logging",
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    install_requires = [
        'setuptools',
        'zc.copy',
        'zc.security',
        'zope.app.keyreference',
    ],
    zip_safe = False
    )
