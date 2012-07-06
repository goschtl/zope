##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import doctest
import unittest
import mock
from zope.testing import setupstack

def side_effect(m, f=None):
    if f is None:
        return lambda f: side_effect(m, f)
    m.side_effect = f

def ebssetup(test):
    volumes = []
    EC2Connection = setupstack.context_manager(
        test, mock.patch('boto.ec2.connection.EC2Connection'))

    class Volume:
        def __init__(self, id, size, zone):
            self.id = id
            self.size = size
            self.zone = zone
            self.tags = {}

    @side_effect(EC2Connection.return_value.create_volume)
    def create_volume(size, zone):
        volume = Volume(str(len(volumes)), size, zone)
        volumes.append(volume)
        return volume

    @side_effect(EC2Connection.return_value.create_tags)
    def create_tags(ids, tags):
        for v in volumes:
            if v.id in ids:
                v.tags.update(tags)

    @side_effect(EC2Connection.return_value.get_all_volumes)
    def get_all_volumes(ids=None):
        if ids is None:
            return list(volumes)
        else:
            return [v for v in volumes if v.id in ids]


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'ebs.test',
            setUp=ebssetup, tearDown=setupstack.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

