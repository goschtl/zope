from setuptools import setup, find_packages

setup(
    name="zc.index",
    version="0.1dev",
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    install_requires = [
        'setuptools',
        'zope.index',
        'BeautifulSoup < 3.0',
        ],
    extras_require=dict(
        test=[
            'zope.app.testing',
            'zope.file',
            ]),
    zip_safe = False
    )
