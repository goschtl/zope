from setuptools import setup, find_packages

setup(
    name='z3c.request',
    version='0.1.0dev',
    url='http://pypi.python.org/pypi/z3c.request',
    license='ZPL 2.1',
    author='Fabio Tranchitella and the Zope Community',
    author_email='zope-dev@zope.org',
    description="Common interface for browser request implementations.",
    long_description=(
        open('src/z3c/request/README.txt').read() + '\n\n' +
        open('CHANGES.txt').read()
    ),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    tests_require=[
        'WebOb',
        'zope.publisher',
        'zope.testing',
    ],
    install_requires=[
        'setuptools',
        'zope.interface',
    ],
    extras_require=dict(
        test=[
            'WebOb',
            'zope.publisher',
            'zope.testing',
        ],
    ),
    include_package_data=True,
    zip_safe=False,
)
