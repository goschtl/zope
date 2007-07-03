from setuptools import setup

setup(
    name="zc.dict",
    version="1.0b1",
    license="ZPL 2.1",
    author="Zope Corporation",
    author_email="zope3-dev@zope.org",

    namespace_packages=["zc"],
    packages=["zc", "zc.dict"],
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=["setuptools", "zope.interface", "ZODB3"],
    tests_require=["zope.testing"],
    description=open('README.txt').read(),
    long_description=open("src/zc/dict/dict.txt").read(),
    keywords="zope zope3",
    zip_safe=False
    )
