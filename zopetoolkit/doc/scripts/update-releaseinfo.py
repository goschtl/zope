# Generate package list information for trunk and tags of ZTK.

import ConfigParser
import StringIO
import os
import os.path
import shutil
import socket
import urllib2
import xml.etree.ElementTree

socket.setdefaulttimeout(10)


TABLE_HEADER = """\
.. list-table::
    :class: packagelist
    :widths: 25 10 40 25
    :header-rows: 1

    * - Name
      - Version
      - Description
      - Links\
"""

PACKAGE_LINE_BASE = """
    * - `%(name)s <%(homepage)s>`_
      - %(version)s
      - %(description)s\
"""

DEPENDENCY_PACKAGE_LINE = PACKAGE_LINE_BASE + """
      - \
"""

PACKAGE_LINE = PACKAGE_LINE_BASE + """
      - `Bugs <http://bugs.launchpad.net/%(name)s>`_ |
        `Subversion <http://svn.zope.org/%(name)s>`_ \
"""

GENERATED_WARNING = """\
.. This file is generated. Please do not edit manually or check in.
"""

DOAP_NS = 'http://usefulinc.com/ns/doap#'
TAGS_DIR = os.path.join(os.pardir, 'tags')

def package_list(packages, config, out,
                 line=PACKAGE_LINE):
    print >>out, TABLE_HEADER
    for package in sorted(packages):
        version = config.get('versions', package)
        doap_xml = urllib2.urlopen(
            'http://pypi.python.org/pypi?:action=doap&name=%s&version=%s' %
            (package, version)).read()
        doap_xml = StringIO.StringIO(doap_xml.replace('\f', ''))
        doap = xml.etree.ElementTree.ElementTree()
        doap.parse(doap_xml)
        description = doap.find('//{%s}shortdesc' % DOAP_NS).text
        homepage = doap.find('//{%s}homepage' % DOAP_NS)
        if homepage:
            homepage = doap.find('//{%s}homepage' % DOAP_NS).get(
                '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', '')
        else:
            # Wah.
            homepage = 'http://pypi.python.org'
        print >>output, line % dict(
            name=package, homepage=homepage, 
            description=description, version=version)
    print >>out


def packages(config, key):
    result = config.get('ztk', key).split('\n')
    result = filter(None, map(str.strip, result))
    return result


releases = [('trunk', os.path.join(os.pardir, 'trunk'))]

for tag in os.listdir(TAGS_DIR):
    if tag.startswith('.'):
        continue
    releases.append((tag, os.path.join(TAGS_DIR, tag)))

for release, location in releases:
    print "Writing package list for", release
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    config.read([os.path.join(location, 'ztk.cfg')])

    output = open(os.path.join('source', 'releases',
                               'packages-%s.rst' % release), 'w')

    print >>output, GENERATED_WARNING

    heading = 'Zope Toolkit %s packages' % release
    print >>output, heading
    print >>output, '=' * len(heading)
    included = packages(config, 'included')
    package_list(included, config, output)

    print >>output, 'Under review'
    print >>output, '------------'
    review = packages(config, 'under-review')
    package_list(review, config, output)

    print >>output, 'Dependencies'
    print >>output, '------------'
    all = config.options('versions')
    dependencies = set(all) - (set(included) | set(review))
    package_list(dependencies, config, output, DEPENDENCY_PACKAGE_LINE)

    output.close()

print "Writing overview"

output = open(os.path.join('source', 'releases', 'index.rst'), 'w')
print >>output, GENERATED_WARNING
print >>output, """
Releases
========

This area collects release-specific information about the toolkit including a
list of backward-incompatible changes, new techniques developed, and libraries
included.

.. toctree::
    :maxdepth: 1

"""

for release, location in releases:
    print >>output, """
    overview-%s\
""" % release


for release, location in releases:
    overview = open(os.path.join('source', 'releases',
                                 'overview-%s.rst' % release), 'w')
    print >>overview, GENERATED_WARNING
    title = "Zope Toolkit %s" % release
    print >>overview, title
    print >>overview, "=" * len(title)
    print >>overview, """
This document covers major changes in this release that can lead to
backward-incompatibilities and explains what to look out for when updating.

.. contents::
    :local:

List of packages
----------------

See the separate `package list <packages-%s.html>`_ document.

""" % release

    overview.write(open(os.path.join(location, 'index.rst')).read())
    overview.close()
