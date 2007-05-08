from setuptools import find_packages, setup

setup(
    name="zope.app.homefolder",
    version="3.4.0b1",
    url="http://svn.zope.org/zope.app.homefolder/",
    license="ZPL 2.1",
    author="Zope Community",
    author_email="zope3-dev@zope.org",
    packages=find_packages("src"),
    namespace_packages=["zope", "zope.app"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "ZODB3",
        "zope.app.container",
        "zope.app.form",
        "zope.app.security",
        "zope.app.zapi",
        "zope.i18nmessageid",
        "zope.dottedname",
        "zope.interface",
        "zope.schema",
        "zope.security",
        "zope.traversing",
        ],
    extras_require={
        "test": [
            "zope.annotation",
            "zope.app.file",
            "zope.app.folder",
            "zope.app.securitypolicy",
            "zope.app.testing",
            "zope.testing",
            ],
        },
    )
