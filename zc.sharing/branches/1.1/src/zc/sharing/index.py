##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

$Id$
"""

import BTrees.IFBTree
import BTrees.OOBTree
import BTrees.IOBTree
import persistent

from zope import component, interface
import zope.security.interfaces
import zope.security.proxy
import zope.index.interfaces

import zope.app.catalog.interfaces
from zope.app import zapi

from zc.sharing import interfaces, policy

class Index(persistent.Persistent):

    interface.implements(zope.app.catalog.interfaces.ICatalogIndex,
                         zope.index.interfaces.IStatistics,
                         )
        
    def __init__(self, privilege_id):
        self.privilege_id = privilege_id
        self.privileges = 1 << privilege_id
        self.clear()
    
    def index_doc(self, doc_id, value):
        self.unindex_doc(doc_id)

        unproxied = zope.security.proxy.removeSecurityProxy(value)
        sharing = interfaces.IBaseSharing(unproxied, None)
        if sharing is None:
            return

        document_principals = self.document_principals
        principal_documents = self.principal_documents

        for principal_id in sharing.getPrincipals():
            if self.privileges & sharing.getBinaryPrivileges(principal_id):
                docs = principal_documents.get(principal_id)
                if docs is None:
                    docs = BTrees.IFBTree.IFTreeSet()
                    principal_documents[principal_id] = docs
                docs.insert(doc_id)

                principals = document_principals.get(doc_id)
                if principals is None:
                    principals = BTrees.OOBTree.OOTreeSet()
                    document_principals[doc_id] = principals
                principals.insert(principal_id)


    def unindex_doc(self, doc_id):
        principals = self.document_principals.get(doc_id)
        if principals is None:
            return

        for principal_id in principals:
            docs = self.principal_documents.get(principal_id)
            if docs and (doc_id in docs):
                docs.remove(doc_id)

        del self.document_principals[doc_id]

    def clear(self):
        self.principal_documents = BTrees.OOBTree.OOBTree()
        self.document_principals = BTrees.IOBTree.IOBTree()

    def apply(self, principal):
        principal_documents = self.principal_documents
        result = principal_documents.get(principal.id)

        groups = {}
        getPrincipal = zapi.principals().getPrincipal
        policy._findGroupsFor(principal, getPrincipal, groups)

        for gid in groups:
            result = BTrees.IFBTree.union(result, principal_documents.get(gid))

        if result is None:
            result = BTrees.IFBTree.IFSet()

        return result

    # XXX need Length objects for scalability
        
    def documentCount(self):
        return len(self.document_principals)        

    def wordCount(self):
        return len(self.principal_documents)

