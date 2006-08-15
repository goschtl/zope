from zope import component

import zc.sharing.policy
import zc.sharing.interfaces
import zope.locking.interfaces
import zc.sharing.sharing
from zope.security.proxy import removeSecurityProxy

class SecurityPolicy(zc.sharing.policy.SecurityPolicy):

    def cachedDecision(self, parent, principal, groups, privilege):
        # Return the decision for a principal and permission

        cache = self.cache(parent)
        try:
            cache_decision = cache.decision
        except AttributeError:
            cache_decision = cache.decision = {}

        cache_decision_prin = cache_decision.get(principal)
        if not cache_decision_prin:
            cache_decision_prin = cache_decision[principal] = {}

        try:
            return cache_decision_prin[privilege]
        except KeyError:
            pass

        sharing = zc.sharing.interfaces.IBaseSharing(parent, None)
        if sharing is not None:
            decision = sharing.sharedTo(privilege, groups)
            # insert new zope.locking code
            if decision and privilege in getPrivileges():
                utility = component.queryUtility(
                    zope.locking.interfaces.ITokenUtility, context=parent)
                if utility is not None:
                    token = utility.get(parent)
                    if token is not None:
                        for p in token.principal_ids:
                            if p in groups:
                                break
                        else:
                            decision = False
            # end new code
        elif parent is None:
            decision = False
        else:
            parent = removeSecurityProxy(getattr(parent, '__parent__', None))
            decision = self.cachedDecision(
                parent, principal, groups, privilege)

        cache_decision_prin[privilege] = decision
        return decision

_privileges = frozenset()

def definePrivilege(bit):
    global _privileges
    tmp = set(_privileges)
    tmp.add(bit)
    _privileges = frozenset(tmp)

def definePrivilegesByTitle(titles):
    assert not isinstance(titles, basestring) # try and avoid a common error
    for title in titles:
        bit = zc.sharing.sharing.getIdByTitle(title)
        definePrivilege(bit) 

def getPrivileges():
    return _privileges

def getPrivilegeTitles():
    return [zc.sharing.sharing.getPrivilege(i)['title'] for i in _privileges]

def removePrivilege(bit):
    global _privileges
    tmp = set(_privileges)
    tmp.remove(bit)
    _privileges = frozenset(tmp)
