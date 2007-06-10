kw = dict(
    name="zc.rebootstrap",
    version="0.2.2",
    author="Zope Corporation and Contributors",
    author_email="zope3-dev@zope.org",
    url="http://svn.zope.org/zc.rebootstrap",
    description=(
        "Helper package to re-bootstrap packages for RPM construction."),
    packages=["zc", "zc.rebootstrap"],
    package_dir={"": "src"},
    )

entry_points = """
[zc.buildout]
default = zc.rebootstrap.bootstrap:Recipe
"""

try:
    from setuptools import setup
    kw["namespace_packages"] = ["zc"]
    kw["zip_safe"] = True
    kw['entry_points'] = entry_points
    kw['namespace_packages'] = ['zc']
except ImportError:
    from distutils.core import setup
    kw["packages"].insert(0, "zc")


setup(**kw)
