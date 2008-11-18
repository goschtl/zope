from setuptools import find_packages, setup

setup(
    name='zcmlschema',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=[
        'zope.app.appsetup',
    ],
    entry_points={'console_scripts': ['generate-schema=zcmlschema.generate:main']}
)
