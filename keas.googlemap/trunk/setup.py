###############################################################################
#
# Copyright 2008 by Keas, Inc., San Francisco, CA
#
###############################################################################
"""Package setup.

$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='keas.googlemap',
    version = '0.5.2-dev',
    author='Paul Carduner, Keas, Inc., and the Zope Community',
    author_email = "zope3-dev@zope.org",
    description='Integration of Google Maps with Zope 3',
    url = 'http://pypi.python.org/pypi/keas.googlemap',
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope google maps",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['keas'],
    extras_require=dict(
        demo = [
            'ZODB3',
            'ZConfig',
            'zc.configuration',
            'zdaemon',
            'zope.publisher',
            'zope.traversing',
            'zope.security',
            'zope.app.wsgi',
            'zope.app.appsetup',
            'zope.app.authentication',
            'zope.app.zcmlfiles',
            'zope.app.securitypolicy',
            'zope.app.twisted',
            'z3c.form',
            'z3c.formui',
            'z3c.pagelet',
            'z3c.layer',
            ],
        test=['zope.app.testing',
              'zope.testing',],
        ),
    install_requires=[
        'setuptools',
        'simplejson>=1.7.3',
        'zope.interface',
        'zope.schema',
        'zope.viewlet',
        ],
    include_package_data = True,
    zip_safe = False,
    )
