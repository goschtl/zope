##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
import sandbox
from zope.security.interfaces import ISecurityPolicy, IChecker
from zope.security import management, checker
from zope.interface import implements

#################################
# 1. map permissions to actions
# 2. map authentication tokens/principals onto permissions
# 3. implement checker and security policies that affect 1,2
# 4. bind checkers to classes/instances
# 5. proxy wrap as nesc.
#################################

#################################
# permissions
NotAllowed = 'Not Allowed'
Public = checker.CheckerPublic
TransportAgent = 'Transport Agent'
AccessServices = 'Access Services'
AccessAgents = 'Access Agents'
AccessTimeService = 'Access Time Services'
AccessAgentService = 'Access Agent Service'
AccessHomeService = 'Access Home Service'

AddAgent = 'Add Agent'
ALL='All'

NoSetAttr = lambda name: NotAllowed

#################################
# location -> auth token -> permission mapping

class SimulationSecurityDatabase:

    origin = {
        'any':[ALL]
        }

    jail = {
        'norse legend':[TransportAgent,
                         AccessServices,
                         AccessAgentService,
                         AccessHomeService,
                         TransportAgent,
                         AccessAgents,],

        'any':[AccessTimeService, AddAgent],

        }

    valhalla = {
        'norse legend':[AddAgent],
        'any': [AccessServices,
               AccessTimeService,
               AccessAgentService,
               AccessHomeService,
               TransportAgent,
               AccessAgents,]
        }


class SimulationSecurityPolicy:

    implements(ISecurityPolicy)

    def checkPermission(self, permission, object, context):
        token = context.user.getAuthenticationToken()
        home = object.getHome()
        db = getattr(SimulationSecurityDatabase, home.getId(), None)

        if db is None:
            return False

        allowed = db.get('any', ())
        if permission in allowed or ALL in allowed:
            return True

        allowed = db.get(token, ())
        if permission in allowed:
            return True

        return False



def PermissionMapChecker(permissions_map={}, setattr_permission_func=NoSetAttr):
    res = {}
    for k,v in permissions_map.items():
        for iv in v:
            res[iv]=k
    return checker.Checker(res.get, setattr_permission_func)


#################################
# sandbox security settings
sandbox_security = {AccessServices:['getService', 'addService', 'getServiceIds'],
                    AccessAgents:['getAgentsIds', 'getAgents'],
                    AddAgent:['addAgent'],
                    TransportAgent:['transportAgent'],
                    Public:['getId','getHome']
                    }
sandbox_checker = PermissionMapChecker(sandbox_security)

#################################
# service security settings

# time service
tservice_security = { AccessTimeService:['getTime'] }
time_service_checker = PermissionMapChecker(tservice_security)

# home service
hservice_security = { AccessHomeService:['getAvailableHomes'] }
home_service_checker = PermissionMapChecker(hservice_security)

# agent service
aservice_security = { AccessAgentService:['getLocalAgents'] }
agent_service_checker = PermissionMapChecker(aservice_security)


def wire_security():

    management.setSecurityPolicy(SimulationSecurityPolicy())

    import zope.security.examples.sandbox

    checker.defineChecker(sandbox.Sandbox, sandbox_checker)
    checker.defineChecker(sandbox.TimeService, time_service_checker)
    checker.defineChecker(sandbox.AgentDiscoveryService, agent_service_checker)
    checker.defineChecker(sandbox.HomeDiscoveryService, home_service_checker)

    def addAgent(self, agent):
        if not self._agents.has_key(agent.getId()) \
           and sandbox.IAgent.isImplementedBy(agent):
            self._agents[agent.getId()]=agent
            checker = checker.selectChecker(self)
            wrapped_home = checker.proxy(self)
            agent.setHome(wrapped_home)
        else:
            raise SandboxError("couldn't add agent %s"%agent)

    sandbox.Sandbox.addAgent = addAgent

    def setupAgent(self, agent):
        management.newSecurityManager(agent)

    sandbox.TimeGenerator.setupAgent = setupAgent

    def GreenerPastures(agent):
        """ where do they want to go today """
        import whrandom
        _homes = sandbox._homes
        possible_homes = _homes.keys()
        possible_homes.remove(agent.getHome().getId())
        new_home =  _homes.get(whrandom.choice(possible_homes))
        return checker.selectChecker(new_home).proxy(new_home)

    sandbox.GreenerPastures = GreenerPastures


if __name__ == '__main__':
    wire_security()
    sandbox.main()
