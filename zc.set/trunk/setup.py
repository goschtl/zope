from setuptools import setup, find_packages
import os.path

def read(path):
    return open(
        os.path.join(os.path.dirname(__file__), *path.split('/'))).read()


setup(
    name="zc.set",
    version="0.1dev",
    license='ZPL 2.1',
    long_description='\n\n'.join([
        read('CHANGES.txt'),
        read('src/zc/set/README.txt'),
        ]),
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'ZODB3',
        'zope.app.folder',
    ],
    extras_require=dict(
        test=[
            'zope.testing',
            ]),
    zip_safe=False
    )
