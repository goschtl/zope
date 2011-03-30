from setuptools import setup, find_packages

setup(
    name="zc.notification",
    version="0.1dev",
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    install_requires = [
        'setuptools',
        'zope.component',
        'zope.schema',
        'zope.i18nmessageid',
        'zope.app.container',
        ],
    extras_require=dict(
        test=[
            'zope.testing',
            'zope.app.testing',
            'zope.app.security',
            'zope.sendmail',
            ]),
    zip_safe = False
    )
