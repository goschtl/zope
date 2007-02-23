kw = dict(
    name="zc.rebootstrap",
    version="0.2",
    author="Zope Corporation and Contributors",
    author_email="zope3-dev@zope.org",
    url="http://svn.zope.org/zc.rebootstrap",
    description=(
        "Helper package to re-bootstrap packages for RPM construction."),
    packages=["zc.rebootstrap"],
    package_dir={"": "src"},
    )

try:
    from setuptools import setup
    kw["namespace_packages"] = ["zc"]
    kw["zip_safe"] = True
except ImportError:
    from distutils.core import setup
    kw["packages"].insert(0, "zc")


setup(**kw)
