from setuptools import setup, find_packages

setup(
    name="zc.sourcefactory",
    version="0.2",
    author="Zope Corporation and Contributors",
    author_email="zope3-dev@zope.org",
    url="http://svn.zope.org/zc.sourcefactory",

    long_description="An easy way to create custom Zope 3 sources.",

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
