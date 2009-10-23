from setuptools import setup, find_packages
import os.path

version = '1.0'

setup(
    name='ZPublisherEventsBackport',
    version=version,
    description="Backport publication events from Zope 2.12 ZPublisher to Zope 2.10",
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='',
    url='',
    author='Laurence Rowe',
    author_email='laurence@lrowe.co.uk',
    license='ZPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        ],
    )

