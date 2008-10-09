from setuptools import setup, find_packages

setup(
    name='hurry.zopeyui',
    version='0.1dev',
    description="Zope integration for YUI.",
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.zoperesource',
        'hurry.yui',
        ],
    )
