from setuptools import setup

entry_points = """\

[zc.buildout]
default=zc.sshtunnel.recipe:Recipe

"""

setup(
    name="zc.sshtunnel",
    packages=["zc.sshtunnel"],
    package_dir={"": "src"},
    namespace_packages=["zc"],
    install_requires=["setuptools"],
    entry_points=entry_points,
    extras_require={"test": "zc.buildout"},
    include_package_data=True,
    zip_safe=False,
    )
