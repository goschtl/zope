from setuptools import setup, find_packages

setup(
    name="zc.copy",
    version="1.3dev",
    install_requires=[
        'setuptools',
        'zope.copy',
        'zope.copypastemove>=3.5.1',
        'zope.location>=3.5.3',
        ],
    extras_require=dict(
        test=[
            'zope.testing',
            ]),
    packages=find_packages('src'),
    include_package_data=True,
    package_dir= {'':'src'},

    namespace_packages=['zc'],

    zip_safe=False,
    author='Zope Project',
    author_email='zope-dev@zope.org',
    description='Pluggable object copying (deprecated in favor of zope.copy)',
    long_description=open("README.txt").read(),
    license='ZPL 2.1',
    keywords="zope zope3 copy clone",
    )
