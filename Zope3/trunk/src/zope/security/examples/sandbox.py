import time, whrandom

from zope.interface import Interface

class IAgent(Interface):
    """
    represents an autonomous unit, that lives in
    various homes/sandboxes and accesses services
    present at the sandboxes. agents are imbued with
    a sense of wanderlust and attempt to find new homes
    after a few turns of the time generator
    (think turn based games).
    """

    def action():
        " agent performs their action "
    def setHome(self, home):
        " agent moves from home to home"
    def getHome():
        " where does this agent live "
    def getAuthenticationToken(self):
        " by what authority should the agent perform actions "

class IService(Interface):
    """
    marker interface. services are available from sandboxes,
    examples include time service, agent discovery, and sandbox
    discovery.
    """

class ISandbox(Interface):
    """
    a container for agents and services.
    """
    def getService(service_id):
        " retrieve a service offered by this sandbox "
    def getAgents():
        " what agents live in this sandbox "
    def addAgent(agent):
        " add an agent to this sandbox "
    def transportAgent(agent, destination):
        " move an agent to the destination sandbox "

class Identity:
    """
    mixin for pretty printing and identity method
    """
    def __init__(self, id, *args, **kw):
        self.id = id
    def getId(self):
        return self.id
    def __str__ (self):
        return "<%s> %s"%(str(self.__class__.__name__), str(self.id))
    __repr__ = __str__

class Agent(Identity):
    """
    see IAgent doc
    """
    __implements__ = IAgent

    def __init__(self, id, home, auth_token, action):
        self.id = id
        self.auth_token = auth_token
        self.home = home
        self._action = action

    def action(self):
        self._action(self, self.getHome())

    def setHome(self, home):
        self.home = home

    def getHome(self):
        return self.home

    def getAuthenticationToken(self):
        return self.auth_token

class SandboxError(Exception): pass

class Sandbox(Identity):
    """
    see ISandbox doc
    """
    __implements__ = ISandbox

    def __init__(self, id, service_factories):
        self.id = id
        self._services = {}
        self._agents = {}

        for sf in service_factories:
            self.addService(sf())

    def getAgentIds(self):
        return self._agents.keys()
    def getAgents(self):
        return self._agents.values()
    def getServiceIds(self):
        return self._services.keys()
    def getService(self, sid):
        return self._services.get(sid)
    def getHome(self):
        return self


    def addAgent(self, agent):
        if not self._agents.has_key(agent.getId()) \
           and IAgent.isImplementedBy(agent):
            self._agents[agent.getId()]=agent
            agent.setHome(self)
        else:
            raise SandboxError("couldn't add agent %s"%agent)

    def addService(self, service):

        if not self._services.has_key(service.getId()) \
           and IService.isImplementedBy(service):
            self._services[service.getId()]=service
            service.setHome(self)
        else:
            raise SandboxError("couldn't add service %s"%service)

    def transportAgent(self, agent, destination):
        if self._agents.has_key(agent.getId()) \
            and destination is not self \
            and ISandbox.isImplementedBy(destination):
            destination.addAgent(agent)
            del self._agents[agent.getId()]
        else:
            raise SandboxError("couldn't transport agent %s to %s"%(
                agent, destination)
                               )

class Service:
    __implements__ = IService
    def getId(self):
        return self.__class__.__name__
    def setHome(self, home):
        self._home = home
    def getHome(self):
        return getattr(self, '_home')

class HomeDiscoveryService(Service):
    """
    returns the ids of available agent homes
    """
    def getAvailableHomes(self):
        return _homes.keys()

class AgentDiscoveryService(Service):
    """
    returns the agents available at a given home
    """
    def getLocalAgents(self, home):
        return home.getAgents()

class TimeService(Service):
    """
    returns the local time
    """
    def getTime(self):
        return time.time()

default_service_factories = (
    HomeDiscoveryService,
    AgentDiscoveryService,
    TimeService
    )

def action_find_homes(agent, home):
    home_service = home.getService('HomeDiscoveryService')
    return home_service.getAvailableHomes()

def action_find_neighbors(agent, home):
    agent_service = home.getService('AgentDiscoveryService')
    return agent_service.getLocalAgents(home)

def action_find_time(agent, home):
    time_service = home.getService('TimeService')
    return time_service.getTime()

class TimeGenerator:
    """
    Represents the passage of time in the agent simulation.

    each turn represents some discrete unit of time, during
    which all agents attempt to perform their action. Additionally,
    all agents are checked to see if they have a desire to move,
    and if so are transported to a new random home.
    """

    def setupAgent(self, agent):
        pass

    def turn(self):

        global _homes

        for h in _homes.values():
            agents = h.getAgents()
            for a in agents:
                self.setupAgent(a)
                try:
                    a.action()
                except Exception, e:
                    print a, h, e

            agents = filter(WanderLust, agents)

            for a in agents:
                try:
                    self.setupAgent(a)
                    home = a.getHome()
                    new_home = GreenerPastures(a)
                    home.transportAgent(a, new_home)
                except Exception, e:
                    print 'moving', a, h, new_home, e

def WanderLust(agent):
    """ is agent ready to move """
    if int(whrandom.random()*100) <= 30:
        return 1

def GreenerPastures(agent):
    """ where do they want to go today """
    global _homes
    possible_homes = _homes.keys()
    possible_homes.remove(agent.getHome().getId())
    return _homes.get(whrandom.choice(possible_homes))


# boot strap initial setup.

# global list of homes
_homes = {}

all_homes = (
    Sandbox('jail', default_service_factories),
    Sandbox('origin', default_service_factories),
    Sandbox('valhalla', default_service_factories)
)

origin = all_homes[1]

for h in all_homes:
    _homes[h.getId()]=h


agents = [
    Agent('odin', None, 'norse legend', action_find_time),
    Agent('loki', None, 'norse legend', action_find_neighbors),
    Agent('thor', None, 'norse legend', action_find_homes),
    Agent('thucydides', None, 'greek men', action_find_time),
    Agent('archimedes', None, 'greek men', action_find_neighbors),
    Agent('prometheus', None, 'greek men', action_find_homes),
    ]

for a in agents:
    origin.addAgent(a)


def main():
    world = TimeGenerator()

    for x in range(5):
        print 'world turning'
        world.turn()

    for h in _homes.values():
        print h.getId(), h.getAgentIds()

if __name__ == '__main__':
    main()
