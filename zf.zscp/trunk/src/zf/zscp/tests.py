##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Viewlet tests

$Id$
"""
__docformat__ = 'restructuredtext'
import os
import unittest
import StringIO
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite, pprint

class Directory(dict):

    def checkout(self, target, svnPath):
        os.mkdir(target)
        # Write a local .svn file that stores the target data.
        svnFile = file(os.path.join(target, '.svn'), 'w')
        svnFile.write(svnPath)
        svnFile.close()
        # Now recurse through the sub directories
        for name, value in self.items():
            path = os.path.join(target, name)
            value.checkout(path, os.path.join(svnPath, name))

    def checkin(self, localPath):
        for name, value in self.items():
            path = os.path.join(localPath, name)
            value.checkin(path)

    def update(self, localPath):
        if not os.path.exists(localPath):
            os.mkdir(localPath)
        for name, value in self.items():
            fullPath = os.path.join(localPath, name)
            value.update(fullPath)


class File(StringIO.StringIO):

    def checkout(self, target, svnPath):
        f = file(target, 'w')
        f.write(self.getvalue())
        f.close()

    def checkin(self, localPath):
        f = file(localPath, 'r')
        self.__init__(f.read())
        f.close()

    def update(self, localPath):
        f = file(localPath, 'w')
        f.write(self.getvalue())
        f.close()


class SVNTestClient(object):

    root = None
    dir = None
    adds = []

    def _getSVNPath(self, svnDir):
        local_path = svnDir.replace(self.root, '')
        obj = self.dir
        for segment in local_path.split('/'):
            if segment == '':
                continue
            obj = obj[segment]
        return obj

    def checkout(self, svnDir, localDir):
        obj = self._getSVNPath(svnDir)
        obj.checkout(localDir, svnDir)

    def checkin(self, localDir, message):
        while self.adds:
            dir = self.adds.pop()
            baseDir, name = os.path.split(dir)
            svnPath = file(os.path.join(baseDir, '.svn'), 'r').read()
            obj = self._getSVNPath(svnPath)
            if os.path.isdir(dir):
                obj[name] = Directory()
            else:
                f = file(dir)
                obj[name] = File(f.read())
                f.close()

        svnPath = file(os.path.join(localDir, '.svn'), 'r').read()
        self._getSVNPath(svnPath).checkin(localDir)

    def update(self, localDir):
        svnPath = file(os.path.join(localDir, '.svn'), 'r').read()
        obj = self._getSVNPath(svnPath)
        obj.update(localDir)

    def ls(self, svnDir):
        obj = self._getSVNPath(svnDir)
        return [{'name': svnDir + '/' + name} for name in obj]

    def mkdir(self, svnDir, message):
        svnDir, name = os.path.split(svnDir)
        obj = self._getSVNPath(svnDir)
        obj[name] = Directory()

    def add(self, files):
        if isinstance(files, list):
            self.adds += files
        else:
            self.adds.append(files)

    def remove(self, svnPath):
        svnDir, name = os.path.split(svnPath)
        obj = self._getSVNPath(svnDir)
        del obj[name]


ZSCP_cfg = '''\
publication PUBLICATION.cfg
certifications CERTIFICATIONS.xml
releases RELEASES.xml
'''

PUBLICATION_cfg = '''\
Package-name: zope.sample
Name: Sample Package
Summary: This is the Sample Package.
Author: John Doe
Author-email: john@doe.com
License: ZPL 2.1
Metadata-version: 1.0
'''

RELEASES_xml = '''\
<releases>
  <release>
   <name>Sample Package</name>
   <version>0.9.0</version>
   <date>2006-02-03</date>
   <certification>level1</certification>
   <package>http://www.zope.org/SamplePackage/Sample-0.9.0.tgz</package>
 </release>
</releases>
'''

CERTIFICATIONS_xml = '''\
<certifications>
  <certification>
    <action>grant</action>
    <source-level>none</source-level>
    <target-level>listed</target-level>
    <date>2006-01-01</date>
    <certification-manager>
      <name>John Doe</name>
      <email>john@doe.com</email>
    </certification-manager>
  </certification>
</certifications>
'''

def zscpSetUp(test):
    client = SVNTestClient()

    client.dir = Directory()
    client.dir['zope.sample'] = Directory()
    client.dir['zope.sample']['zscp'] = Directory()
    client.dir['zope.sample']['zscp']['ZSCP.cfg'] = File(ZSCP_cfg)
    client.dir['zope.sample']['zscp']['PUBLICATION.cfg'] = File(PUBLICATION_cfg)
    client.dir['zope.sample']['zscp']['RELEASES.xml'] = File(RELEASES_xml)
    client.dir['zope.sample']['zscp']['CERTIFICATIONS.xml'] = File(
        CERTIFICATIONS_xml)
    client.dir['zope.sample1'] = Directory()
    client.dir['zope.sample2'] = Directory()

    test.globs['svnClient'] = client

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('release.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('certification.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('publication.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('zscp.txt',
                     setUp=zscpSetUp,
                     globs={'pprint': pprint},
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
