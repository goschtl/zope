# Setup for zc.iso8601.

import os
import setuptools


def read(path):
    return open(path).read()


def long_description():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = [os.path.join(here, "src/zc/iso8601", fn)
             for fn in "README.txt", "CHANGES.txt"]
    return "\n\n".join([open(path).read() for path in paths])


setuptools.setup(
    name="zc.iso8601",
    version="0.1.0dev",
    description="ISO 8601 utility functions",
    url="http://pypi.python.org/pypi/zc.iso8601/",
    long_description=long_description(),
    author="Fred Drake",
    author_email="fdrake@gmail.com",
    license="ZPL 2.1",
    classifiers=[
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        ],
    platforms="any",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    namespace_packages=["zc"],
    install_requires=[
        "pytz",
        "setuptools",
        "zope.testing",
        ],
    zip_safe=False,
    )
