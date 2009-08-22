from setuptools import setup, find_packages

setup(
    name='z3c.bobopublisher',
    version='0.1.3',
    url='http://pypi.python.org/pypi/z3c.bobopublisher',
    license='ZPL 2.1',
    author='Fabio Tranchitella',
    author_email='fabio@tranchitella.it',
    description="Minimal reimplementation of the Zope publisher using the bobo framework.",
    long_description=(
        open('src/z3c/bobopublisher/README.txt').read() + '\n\n' +
        open('CHANGES.txt').read()
    ),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    tests_require=[
        'webtest',
        'zope.testing',
    ],
    install_requires=[
        'setuptools',
        'bobo',
        'WebOb',
        'z3c.request',
        'zope.browser',
        'zope.component',
        'zope.configuration',
        'zope.dottedname',
        'zope.interface',
        'zope.location',
        'zope.schema',
        'zope.security',
    ],
    extras_require=dict(
        test=[
            'webtest',
            'zope.testing',
        ],
    ),
    entry_points="""
    [paste.app_factory]
    main = z3c.bobopublisher.application:Application
    [paste.filter_app_factory]
    proxy = z3c.bobopublisher.middleware.proxy:make_proxy_middleware
    security = z3c.bobopublisher.middleware.security:make_security_middleware
    """,
    include_package_data=True,
    zip_safe=False,
)
