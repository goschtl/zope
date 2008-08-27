from setuptools import setup, find_packages
import os.path

def read_file(*args):
    return open(os.path.join(os.path.dirname(__file__), *args), "r").read()


setup(
    name="zc.sourcefactory",
    version="0.4.0dev",
    author="Zope Corporation and Contributors",
    author_email="zope3-dev@zope.org",
    url="http://svn.zope.org/zc.sourcefactory",

    description="An easy way to create custom Zope 3 sources.",

    long_description=(
        read_file("src", "zc", "sourcefactory", "README.txt") +
        "\n\n" + 
        read_file("src", "zc", "sourcefactory", "mapping.txt") +
        "\n\n" + 
        read_file("src", "zc", "sourcefactory", "constructors.txt") +
        "\n\n" + 
        read_file("src", "zc", "sourcefactory", "adapters.txt") +
        "\n\n" + 
        read_file("src", "zc", "sourcefactory", "browser", "README.txt") +
        "\n\n" + 
        read_file("src", "zc", "sourcefactory", "browser", "token.txt") +
        "\n\n" + 
        read_file("CHANGES.txt")
        ),

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
