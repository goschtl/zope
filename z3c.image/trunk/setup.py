from setuptools import setup, find_packages

setup(
    name = "z3c.image",
    version = "0.1",
    author = "Zope Contributors",
    author_email = "office@mopacreative.com",
    description = "Image utils for zope3",
    license = "ZPL 2.1",
    keywords = "zope3 image",
    url='http://svn.zope.org/z3c.image',
    classifiers = [
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: Zope Public License",
        "Framework :: Zope :: UI",
        ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    # 'PILwoTk' is a package containing a version of PIL that doesn't
    # magically sniff for the Tk installation.
    install_requires=['setuptools', 'PILwoTk'],
    extras_require={"test": ["zope.app.testing"]},
    zip_safe=False,
    )
