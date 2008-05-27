import os
from setuptools import setup, find_packages

setup(
    name="lovely.zetup",
    version="0.0.0",
    zip_safe = False,
    include_package_data = True,
    packages = find_packages('src'),
    namespace_packages=['lovely'],
    extras_require = dict(
        test = ['zope.testing',
                'zope.app.authentication',
                #'zc.testbrowser'
                ]
        ),
    install_requires = ['setuptools',
                        'zope.interface',
                        'zope.component',
                        'zope.schema',
                        'zope.event',
                        'zope.error',
                        'zope.app.component',
                        'wsgi_intercept',
                        #'zope.app.zcmlfiles',
                        'transaction',
                        #'zope.app.securitypolicy',
                        'Paste',
                        'PasteDeploy',
                        'z3c.configurator',
                        ],
    package_dir = {'':'src'},
    entry_points = """
    [paste.app_factory]
    main = lovely.zetup.factory:app_factory
    """
    )
