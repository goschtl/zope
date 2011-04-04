from setuptools import setup, find_packages

setup(
    name="zc.preview",
    version="0.1dev",
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'zope.file',
        'zope.mimetype',
        'zc.shortcut',  # only needed for tests?
        ],
    extras_require=dict(
        test=[
            'zope.app.debugskin',
            'zope.app.server',
            'zope.app.testing',
            'zope.app.zcmlfiles',
            ]),

    zip_safe=False,
    )
