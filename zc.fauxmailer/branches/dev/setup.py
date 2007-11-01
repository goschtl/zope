from setuptools import setup, find_packages

setup(
    name = "zc.fauxmailer",
    description = "Simple printing mailer for development",
    version = "0.2",
    license = "ZPL",
    packages = find_packages('src'),
    include_package_data = True,
    zip_safe = False,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
        'setuptools',
        'zope.interface',
        'zope.sendmail',
        ],
    )
