from setuptools import setup, find_packages

setup(
    name="bluebream",
    version="0.1dev",
    author="Baiju M",
    author_email="baiju.m.mail@gmail.com",
    url="https://launchpad.net/grokproject",
    download_url="http://pypi.python.org/pypi/grokproject",
    description="Script to setup a Zope project directory.",
    license="Simplified BSD License",
    packages=find_packages("src"),
    package_dir={"": "src"},
    zip_safe=False,
    install_requires=["PasteScript>=1.7.3"],
    entry_points={
    "console_scripts": ["bluebream = bluebream.script:main"],
    "paste.paster_create_template": ["bluebream = bluebream.template:BlueBream"]},
    )
