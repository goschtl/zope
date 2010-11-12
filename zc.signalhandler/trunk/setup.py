from setuptools import find_packages, setup

setup(
    name="zc.signalhandler",
    version="1.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["ZConfig >= 2.4a3"],
    include_package_data=True,
    zip_safe=False,
    )
