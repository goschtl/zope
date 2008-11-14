import os
from setuptools import setup, find_packages

setup(
    name="lovely.zetup",
    version="0.1.0a1",
    zip_safe = False,
    include_package_data = True,
    packages = find_packages('src'),
    namespace_packages=['lovely'],
    url = 'http://svn.zope.org/lovely.zetup',
    extras_require = dict(
        test = ['zope.testing',
                'zope.app.authentication',
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
                        'transaction',
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
