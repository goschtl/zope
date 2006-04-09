##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""ZSCP Data Management

$Id$
"""
__docformat__ = "reStructuredText"
import os
import os.path
import pysvn
import zope.event
import zope.interface

from zf.zscp import interfaces, package, publication, release, certification


class ZSCPRepository(object):
    """A ZSCP-compliant repository."""
    zope.interface.implements(interfaces.IZSCPRepository)

    def __init__(self, svnRoot, localRoot, password):
        self.svnRoot = svnRoot
        self.localRoot = localRoot
        self.password = password

    def _getClient(self):
        """Get an SVN client."""
        client = pysvn.Client()

        def ssl_password(realm, may_save):
            return True, self.password, True
        client.callback_ssl_client_cert_password_prompt = ssl_password

        return client

    def initialize(self):
        """See interfaces.IZSCPRepository"""
        client = self._getClient()
        # for each package that is already part of the ZSCP, make sure to
        # check out the ZSCP data.
        for name in self.fetch():
            full_url = self.svnRoot + '/' + name + '/zscp'
            local_path = os.path.join(self.localRoot, name)
            client.checkout(full_url, local_path)
        # Send out an event notification
        zope.event.notify(interfaces.RepositoryInitializedEvent(self))

    def register(self, pkg):
        """See interfaces.IZSCPRepository"""
        client = self._getClient()
        full_url = self.svnRoot + '/' + pkg.name + '/zscp'
        local_path = os.path.join(self.localRoot, pkg.name)
        # Create a directory for zscp remotely
        client.mkdir(full_url, 'Create a directory for the ZSCP process.')
        # Check out the directory
        client.checkout(full_url, local_path)
        # Create a ZSCP.cfg file
        zscp = {'publication': 'PUBLICATION.cfg',
                'releases': 'RELEASES.xml',
                'certifications': 'CERTIFICATIONS.xml'}
        zscp_file = file(os.path.join(local_path, 'ZSCP.cfg'), 'w')
        zscp_file.write(produce(zscp))
        zscp_file.close()
        # Now update that data
        self.update(pkg)
        # Add all files to the repository and check them in
        client.add([os.path.join(local_path, 'ZSCP.cfg'),
                    os.path.join(local_path, 'PUBLICATION.cfg'),
                    os.path.join(local_path, 'RELEASES.xml'),
                    os.path.join(local_path, 'CERTIFICATIONS.xml')])
        client.checkin(local_path, 'Initial addition of package data.')
        # Send out an event notification
        zope.event.notify(interfaces.PackageRegisteredEvent(pkg))

    def unregister(self, pkg):
        """See interfaces.IZSCPRepository"""
        client = self._getClient()
        full_url = self.svnRoot + '/' + pkg.name + '/zscp'
        # Remove the directory
        client.remove(full_url)
        # Remove local checkout
        # LAME! Simulate recursive delete!
        def remove(arg, dirname, fnames):
            for fname in fnames:
                path = os.path.join(dirname, fname)
                if os.path.isfile(path):
                    os.remove(path)

        os.path.walk(os.path.join(self.localRoot, pkg.name), remove, None)
        os.removedirs(os.path.join(self.localRoot, pkg.name))
        # Send out an event notification
        zope.event.notify(interfaces.PackageUnregisteredEvent(pkg))

    def update(self, pkg):
        """See interfaces.IZSCPRepository"""
        client = self._getClient()
        local_path = os.path.join(self.localRoot, pkg.name)
        # Do checkout update
        client.update(local_path)
        # Load the ZSCP configuration
        zscp_path = os.path.join(local_path, 'ZSCP.cfg')
        zscp = process(file(zscp_path))
        # Update publication
        pub_file = file(os.path.join(local_path, zscp['publication']), 'w')
        pub_file.write(publication.produce(pkg.publication))
        pub_file.close()
        # Update releases
        rel_file = file(os.path.join(local_path, zscp['releases']), 'w')
        rel_file.write(release.produceXML(pkg.releases))
        rel_file.close()
        # Update certifications
        cert_file = file(os.path.join(local_path, zscp['certifications']), 'w')
        cert_file.write(certification.produceXML(pkg.certifications))
        cert_file.close()
        # Commit the changes
        client.checkin(local_path, 'Update of package data.')
        # Send out an event notification
        zope.event.notify(interfaces.PackageUpdatedEvent(pkg))

    def fetch(self, all=False):
        """See interfaces.IZSCPRepository"""
        names = []
        client = self._getClient()
        for entry in client.ls(self.svnRoot):
            name = os.path.split(entry['name'])[-1]
            if all is True:
                names.append(name)
            else:
                path = entry['name'] + '/zscp'
                if path in [e['name'] for e in client.ls(entry['name'])]:
                    names.append(name)
        return names

    def __getitem__(self, key):
        """See zope.interface.common.mapping.IItemMapping"""
        if key not in os.listdir(self.localRoot):
            raise KeyError, key

        local_path = os.path.join(self.localRoot, key)
        # Load the ZSCP configuration
        zscp_path = os.path.join(local_path, 'ZSCP.cfg')
        zscp = process(file(zscp_path))
        # Create the package
        pkg = package.Package(key)
        # Add publication
        pub_file = file(os.path.join(local_path, zscp['publication']), 'r')
        pkg.publication = publication.process(pub_file)
        pub_file.close()
        # Add releases
        rel_file = file(os.path.join(local_path, zscp['releases']), 'r')
        pkg.releases = release.processXML(rel_file)
        rel_file.close()
        # Add certifications
        cert_file = file(os.path.join(local_path, zscp['certifications']), 'r')
        pkg.certifications = certification.processXML(cert_file)
        cert_file.close()

        return pkg

    def keys(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        return os.listdir(self.localRoot)

    def get(self, key, default=None):
        """See zope.interface.common.mapping.IReadMapping"""
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        """See zope.interface.common.mapping.IReadMapping"""
        return key in self.keys()

    def __iter__(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        return iter(keys)

    def values(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        return [self[name] for name in self.keys()]

    def items(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        return [(name, self[name]) for name in self.keys()]

    def __len__(self):
        """See zope.interface.common.mapping.IEnumerableMapping"""
        return len(self.keys())


def process(file):
    """Process the ZSCP.cfg file content."""
    config = {}
    for line in file.readlines():
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        key, value = line.split(' ')
        config[key] = value
    return config

def produce(zscp):
    """Produce the ZSCP.cfg file content."""
    return '\n'.join(['%s %s' %(key, value) for key, value in zscp.items()])
