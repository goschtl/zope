import os
from setuptools.extension import Extension
from setuptools import setup, find_packages

long_description = (open("src/zc/twist/README.txt").read() +
                    '\n\n=======\nChanges\n=======\n\n' +
                    open("CHANGES.txt").read())

methodwrapper = Extension(
    name='zc.twist._methodwrapper',
    sources=[os.path.join('src','zc','twist','_methodwrapper.c')],
    )

setup(
    name='zc.twist',
    version='1.2',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Zope Project',
    author_email='zope-dev@zope.org',
    description=open('README.txt').read(),
    long_description=long_description,
    license='ZPL',
    install_requires=[
        'ZODB3',
        'Twisted>=8.0.1', # 8.0 was setuptools compatible
        'zope.component',
        'setuptools',
        'zope.testing',
        ],
    include_package_data=True,
    ext_modules=[methodwrapper],
    )
