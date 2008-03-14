
from distutils.extension import Extension
from setuptools import setup, find_packages

long_description = (open("src/zc/twist/README.txt").read() +
                    '\n\n=======\nChanges\n=======\n\n' +
                    open("CHANGES.txt").read())

methodwrapper = Extension(
    name='zc.twist._methodwrapper',
    sources=['src/zc/twist/_methodwrapper.c'],
    )

setup(
    name='zc.twist',
    version='1.0.1',
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
        'zc.twisted', # setup-friendly Twisted distro.  Someday soon we can
        # discard zc.twisted, hopefully.  See
        # http://twistedmatrix.com/trac/ticket/1286
        'zope.component',
        'setuptools',
        'zope.testing',
        ],
    include_package_data=True,
    ext_modules=[methodwrapper],
    )
