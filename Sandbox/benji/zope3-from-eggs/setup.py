import os

from setuptools import setup, find_packages

setup(
    name='zope3-from-eggs',
    version='1.0',
    packages=find_packages('src', exclude=['*.tests', '*.ftests']),
    package_dir={'':'src'},

    url='http://svn.zope.com/home/benji/zope3-from-eggs',
    zip_safe=False,
    author='Zope Corporation',
    author_email='sales@zope.com',
    description='A Zope 3 from only eggs',
    license='ZVSL',
    install_requires=[
        'ZODB3',
        'setuptools',
        'zope.app.securitypolicy',
        'zope.app.server',
        'zope.app.zcmlfiles',
        'zope.testbrowser',
        'zope.testing',
        ],
    include_package_data=True,
    )
