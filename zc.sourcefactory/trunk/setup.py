from setuptools import setup, find_packages

setup(
    name="zc.sourcefactory",
    version="0.1dev",
    packages=find_packages('src'),
    package_dir={'':'src'},
    include_package_data=True,
    install_requires=["setuptools"],
    namespace_packages=['zc'],
    zip_safe=False
    )
