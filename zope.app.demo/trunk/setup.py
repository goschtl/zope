from setuptools import setup, find_packages
import os

setup(
    name="zope.app.demo",
    version="3.4.0b1",
    author="Zope Corporation and Contributors",
    author_email="zope3-dev@zope.org",
    url="http://svn.zope.org/zope.app.demo",

    description="A collection of demo packages for Zope 3",
    packages=find_packages('src'),
    package_dir={'':'src'},

    include_package_data=True,
    install_requires=["setuptools",
                      "ZODB3",
                      "zope.app.basicskin",
                      "zope.app.component",
                      "zope.app.component",
                      "zope.app.container",
                      "zope.app.content",
                      "zope.app.folder",
                      "zope.app.i18n",
                      "zope.app.pagetemplate",
                      "zope.app.pluggableauth",
                      "zope.app.preference",
                      "zope.app.publisher",
                      "zope.app.security",
                      "zope.app.zapi",
                      "zope.component",
                      "zope.dublincore",
                      "zope.event",
                      "zope.interface",
                      "zope.lifecycleevent",
                      "zope.location",
                      "zope.publisher",
                      "zope.schema"],

    zip_safe=False
)
