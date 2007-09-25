from setuptools import setup, find_packages

entry_points="""
[console_scripts]
references = zc.fsutil.references:references_script

"""

setup(
    name = "zc.fsutil",
    description = "ZODB Database Utilities",
    version = ".1",
    license = "ZPL",
    packages = find_packages('src'),
    include_package_data = True,
    zip_safe = False,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    entry_points = entry_points,
    install_requires = [
        'setuptools',
        'ZODB3',
        ],
    )
