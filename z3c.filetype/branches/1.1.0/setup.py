from setuptools import setup, find_packages

setup(
    name="z3c.filetype",
    version="1.2.0",
    namespace_packages=["z3c"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "setuptools",
        "zope.cachedescriptors",
        "zope.component",
        "zope.contenttype",
        "zope.event",
        "zope.i18nmessageid",
        "zope.interface",
        "zope.lifecycleevent",
        "zope.proxy",
        "zope.schema",
        "zope.size",
        ],
    extras_require={
        "test": ["zope.testing"],
        },
    zip_safe=False,
    )
