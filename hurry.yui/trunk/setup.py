from setuptools import setup, find_packages

YUI_VERSION = '2.6.0'

setup(
    name='hurry.yui',
    version=YUI_VERSION + 'dev',
    description="YUI for hurry.resource.",
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
        'hurry.resource',
        'simplejson',
        ],
    entry_points= {
    'console_scripts': [
      'yuiprepare = hurry.yui.prepare:main',
      ]
    },

    )
