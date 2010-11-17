from setuptools import setup, find_packages

setup(
    name = 'z3checkins',
    version = '0.1',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope-dev@zope.org',
    description = '',
    license = 'ZPL 2.1',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools',
                        'ZODB3',
                        'zope.app.container',
                        'zope.app.file',
                        'zope.app.form',
                        'zope.app.pagetemplate',
                        'zope.datetime',
                        'zope.dublincore >= 3.7',
                        'zope.interface',
                        'zope.publisher',
                        ],
    extras_require=dict(
        test=[
            'zope.app.testing',
            'zope.app.zcmlfiles',
            ]),
    zip_safe = False,
    )
