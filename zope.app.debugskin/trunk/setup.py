from setuptools import setup, find_packages
import os

setup(
    name="zope.app.debugskin",
    version="3.4.0b1",
    author="Zope Corporation and Contributors",
    author_email="zope3-dev@zope.org",
    url="http://svn.zope.org/zope.app.debugskin",

    description="A collection of demo packages for Zope 3",
    packages=find_packages('src'),
    package_dir={'':'src'},

    include_package_data=True,
    install_requires=["setuptools"],

    zip_safe=False
)
