import zope.security.examples.sandbox

# XXX These imports are wrong and were wrong before the renaming
from zope.security import ISecurityPolicy, Checker, IChecker

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
Public = Checker.CheckerPublic
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

    __implements__ = ISecurityPolicy

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
    return Checker.Checker(res.get, setattr_permission_func)


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

    from zope.security import securitymanagement
    securitymanagement.setSecurityPolicy(SimulationSecurityPolicy())

    import zope.security.examples.sandbox

    Checker.defineChecker(sandbox.Sandbox, sandbox_checker)
    Checker.defineChecker(sandbox.TimeService, time_service_checker)
    Checker.defineChecker(sandbox.AgentDiscoveryService, agent_service_checker)
    Checker.defineChecker(sandbox.HomeDiscoveryService, home_service_checker)

    def addAgent(self, agent):
        if not self._agents.has_key(agent.getId()) \
           and sandbox.IAgent.isImplementedBy(agent):
            self._agents[agent.getId()]=agent
            checker = Checker.selectChecker(self)
            wrapped_home = checker.proxy(self)
            agent.setHome(wrapped_home)
        else:
            raise SandboxError("couldn't add agent %s"%agent)

    sandbox.Sandbox.addAgent = addAgent

    def setupAgent(self, agent):
        SecurityManagement.newSecurityManager(agent)

    sandbox.TimeGenerator.setupAgent = setupAgent

    def GreenerPastures(agent):
        """ where do they want to go today """
        import whrandom
        _homes = sandbox._homes
        possible_homes = _homes.keys()
        possible_homes.remove(agent.getHome().getId())
        new_home =  _homes.get(whrandom.choice(possible_homes))
        return Checker.selectChecker(new_home).proxy(new_home)

    sandbox.GreenerPastures = GreenerPastures


if __name__ == '__main__':
    wire_security()
    sandbox.main()
