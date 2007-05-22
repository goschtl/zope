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
        ],
    namespace_packages=['zc'],
    zip_safe=False,
    )
