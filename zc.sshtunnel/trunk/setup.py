from setuptools import setup

entry_points = """\

[zc.buildout]
default=zc.sshtunnel.recipe:Recipe

"""

setup(
    name="zc.sshtunnel",
    version="1.1",
    description="zc.buildout recipe to manage an SSH tunnel.",
    author="Zope Corporation and contributors",
    author_email="zope3-dev@zope.org",
    packages=["zc", "zc.sshtunnel"],
    package_dir={"": "src"},
    namespace_packages=["zc"],
    install_requires=["setuptools"],
    entry_points=entry_points,
    extras_require={"test": "zc.buildout"},
    include_package_data=True,
    zip_safe=False,
    classifiers=["Framework :: Buildout"],
    )
