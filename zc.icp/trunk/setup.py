from setuptools import setup, find_packages
import os

def read(rname):
    return open(os.path.join(os.path.dirname(__file__), *rname.split('/')
                             )).read()

long_description = '\n\n'.join([
    read('README.txt'),
    '.. contents::',
    read('CHANGES.txt'),
    read('src/zc/icp/README.txt'),
    ])

setup(
    name='zc.icp',
    version='1.1.0dev',
    packages=find_packages('src', exclude=['*.tests', '*.ftests']),
    package_dir={'':'src'},

    url='svn+ssh://svn.zope.com/repos/main/zc.icp',
    zip_safe=False,
    author='Benji York',
    author_email='benji@zope.com',
    description='Small, pluggable ICP (Internet Cache Protocol) server',
    long_description = long_description,
    license='ZPL 2.1',
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.interface',
        'zope.testing',
        ],
    include_package_data=True,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        ],
    )
