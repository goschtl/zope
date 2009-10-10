from setuptools import setup, find_packages

setup(
    name="lms.main",
    version="0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["lms"],
    install_requires=["setuptools",
                      "Zope2"],
    )
