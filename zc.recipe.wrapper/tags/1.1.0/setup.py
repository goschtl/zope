##############################################################################
#
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
import setuptools
from setuptools import setup, find_packages

# generic helpers primarily for the long_description
try:
    import docutils
except ImportError:
    def validateReST(text):
        return ''
else:
    import docutils.utils
    import docutils.parsers.rst
    import StringIO
    def validateReST(text):
        doc = docutils.utils.new_document('validator')
        # our desired settings
        doc.reporter.halt_level = 5
        doc.reporter.report_level = 1
        stream = doc.reporter.stream = StringIO.StringIO()
        # docutils buglets (?)
        doc.settings.tab_width = 2
        doc.settings.pep_references = doc.settings.rfc_references = False
        doc.settings.trim_footnote_reference_space = None
        # and we're off...
        parser = docutils.parsers.rst.Parser()
        parser.parse(text, doc)
        return stream.getvalue()

def text(*args, **kwargs):
    # note: distutils explicitly disallows unicode for setup values :-/
    # http://docs.python.org/dist/meta-data.html
    tmp = []
    for a in args:
        if a.endswith('.txt'):
            f = open(os.path.join(*a.split('/')))
            tmp.append(f.read())
            f.close()
            tmp.append('\n\n')
        else:
            tmp.append(a)
    if len(tmp) == 1:
        res = tmp[0]
    else:
        res = ''.join(tmp)
    out = kwargs.get('out')
    if out is True:
        out = 'TEST_THIS_REST_BEFORE_REGISTERING.txt'
    if out:
        f = open(out, 'w')
        f.write(res)
        f.close()
        report = validateReST(res)
        if report:
            print report
            raise ValueError('ReST validation error')
    return res
# end helpers; below this line should be code custom to this package



ENTRY_POINTS = """
[zc.buildout]
default = zc.recipe.wrapper:Wrapper
"""


setuptools.setup(
    name="zc.recipe.wrapper",
    version="1.1.0",
    description="Recipe that creates shell wrapper scripts",
    long_description=text(
        'CHANGES.txt',
        out=True),
    keywords="development build wrapper generater",
    classifiers = [
       'Framework :: Buildout',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Build Tools',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
    author="Aaron Lehmann",
    author_email="aaron@zope.com",
    license="ZPL 2.1",

    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    namespace_packages=["zc", "zc.recipe"],
    install_requires=[
        "setuptools",
        "zc.recipe.testrunner",
        "zope.testing",
        ],
    include_package_data=True,
    zip_safe=False,
    entry_points=ENTRY_POINTS,
    )
