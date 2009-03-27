%(commentHeader)s
"""Setup"""
from setuptools import setup, find_packages

setup (
    name = '%(name)s',
    version = '%(version)s',
    author = u"%(author)s",
    author_email = u"%(author_email)s",
    description = u"%(description)s",
    license = "%(license)s",
    keywords = u"%(keywords)s",
    url = "%(url)s",
    classifiers = %(classifiers)s,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = [%(namespacePackages)s],
    extras_require = %(extras_require)s,
    install_requires = [
        'setuptools',%(install_requires)s
        ],
    zip_safe = False,
    entry_points = %(entry_points)s,
    )
