from setuptools import setup, find_packages
import os.path

setup(
    name="zc.sourcefactory",
    version="0.3.3",
    author="Zope Corporation and Contributors",
    author_email="zope3-dev@zope.org",
    url="http://svn.zope.org/zc.sourcefactory",

    description="An easy way to create custom Zope 3 sources.",

    long_description=(open(
        os.path.join(os.path.dirname(__file__),
                     "src", "zc", "sourcefactory", "README.txt"),
        "r").read() + "\n\n" + 
        open(os.path.join(os.path.dirname(__file__), "CHANGES.txt"),
             "r").read()),

    packages=find_packages('src'),
    package_dir={'':'src'},

    include_package_data=True,
    install_requires=[
        "setuptools",
        "ZODB3",
        "zope.app.form",
        "zope.app.intid",
        "zope.component",
        "zope.dublincore",
        "zope.interface",
        "zope.proxy",
        "zope.publisher",
        "zope.schema",
        ],
    namespace_packages=['zc'],
    extras_require={
        "test": ["zope.testing",
                 "zope.app.testing",
                 "zope.app.keyreference",
                 "zope.app.zcmlfiles",
                 ]},
    zip_safe=False,
    )
