Zope3 Security

  Introduction

    The Security framework provides a generic mechanism to implement
    security policies on python objects. This introduction provides
    a tutorial of the framework explaining concepts, design, and
    going through sample usage from the perspective of a python 
    programmer using the framework outside of Zope.
    
  Definitions

    Principal

     A generalization of a concept of a user. a principal may be 
     associated with different roles and permissions.

    Permission
     
     A kind of access. ie permission to READ vs. permission to WRITE    
     fundamentally the whole security framework is organized around
     checking permissions on objects.

    Roles

     represents a reposibility of a user in the context of an object.
     Roles are associated with the permissions nesc. to fufill the
     user's responsiblity.

  Purpose

    The security framework's primary purpose is to guard and check
    access to python objects. It does this by providing mechanisms
    for explicit and implicit security checks on attribute access
    for objects. Attribute names are mapped onto permission names when
    checking accesss and the implementation of the security check is 
    defined by the security policy, which recieves the object, the 
    permission name, and a context. 

    Security contexts are containers of transient information such
    as the current principal and the context stack.
    
    To explain the concept and usage of the context stack a little
    background into the design influences of the default zope policy 
    is needed, namely the java language security model. Within the
    base language, code is associated with identifiers. ie this code
    came from joe schmoe, and another code archive comes signed from
    verisign. when executing restricted code, its important access 
    is checked not only for the code currently executing but for the
    entire call/context stack (unless explictly short-circuited). ie 
    if joe schmoe's code does haven't access to the filesystem, but if
    the verisign code does, joe's code could circumvent the security
    policy by accessing the filesystem via the verisign code.
    
    Its important to keep in mind that the policy provided is just
    a default, and it can be substituted with one which doesn't 
    care about principals or context stacks at all.

  Framework Components

    Low Level Components

      These components provide the infrastructure for guarding
      attribute access and providing hooks into the higher level
      security framework.

      Checkers

        a checker is associated with an object kind, and provides
        the hooks that map attribute checks onto permissions
        deferring to the security manager (which in turn defers to the
        policy) to perform the check.

        additionally checkers, provide for creating proxies of objects
        associated with the checker.
        
        there are several implementation variants of checkers 
        from checkers that grant access based on attribute names,
        
      Proxies
      
        Wrappers around python objects that implictly guard 
        access to their wrapped contents by delegating to their
        associated checker. Proxies are also viral in nature,
        in that values returned by proxies are also proxied.
   
    High Level Components

      Security Management

        Provides accessors for setting up security manager
        and global security policy     

      Security Context

        stores transient information on the current principal and
        the context stack.

      Security Manager

        manages security context (execution stack) and delegates
        permission checks to security policy.

      Security Policy

        provides a single method that accepts the object, the
        permission, and the context of the access being checked
        and is used to implement the application logic for 
        the security framework.

  Narrative (agent sandbox)

    As an example we take a look at constructing a multi-agent
    distributed system, and then adding a security layer using 
    the zope security model onto it.

    Scenario

      Our agent simulation consists of autonomous agents that 
      live in various agent homes/sandboxes and perform actions
      that access services available at their current
      home. Agents carry around authentication tokens
      which signify their level of access within any given home.
      Additionally agents attempt to migrate from home to home
      randomly.

      the agent simulation was constructed separately from any 
      security aspects. now we want to define and integrate a 
      security model into the simulation. the full code for 
      the simulation and the security model is available separately
      we present only relevant code snippets here for illustration
      as we go through the implementation process.

      for the agent simulation we want to add a security model such 
      that we group agents into two authentication groups, norse
      legends, including the principals thor, odin, and loki, and
      greek men, including prometheus, archimedes, and thucydides.
      
      we associate permissions with access to services, and homes.
      and differentiate the homes such that certain authentication
      groups only have access to services or the the home itself 
      based on the local settings of the home in which they reside.

      we define the homes/sandboxes

        - origin - all agents start here, and have access to all
          services here.

        - valhalla - only agents in the authentication group 
          'norse legend' can reside here.

        - jail - all agents can come here, but only 'norse legend's
          can leave or access services.


    Process

      loosely we define a process for implementing this security model
      
      - mapping permissions on to actions

      - mapping authentication tokens onto permissions

      - implementing checkers and security policies that use our
        authentication tokens and permissions.

      - binding checkers to our simulation classes

      - inserting the hooks into the original simulation code to add 
        proxy wrappers to automatically check security.
      
      - inserting hooks into the original simulation to register
        the agents as the active principal within a security manager's
        context....

    Defining Permission Model

      We define the following permissions::

       NotAllowed = 'Not Allowed'
       Public = Checker.CheckerPublic
       TransportAgent = 'Transport Agent'
       AccessServices = 'Access Services'
       AccessAgents = 'Access Agents'
       AccessTimeService = 'Access Time Services'
       AccessAgentService = 'Access Agent Service'
       AccessHomeService = 'Access Home Service'      

      and create a dictionary database mapping homes
      to authentication groups which are linked
      to associated permissions.

    Defining and Binding Checkers

      Checkers are the foundational unit for the security framework
      they define what attributes can be accessed or set on a given 
      instance. they can be used implicitly via Proxy objects, to 
      guard all attribute access automatically or explictly to check    
      a given access for an operation.

      Checker construction expects two functions or dictionaries, one
      is used to map attribute names to permissions for attribute
      access and another to do the same for setting attributes.

      We use the following checker factory function::

         def PermissionMapChecker(permissions_map={}, setattr_permission_func=NoSetAttr):
             res = {}
             for k,v in permissions_map.items():
                 for iv in v:
                     res[iv]=k
             return Checker.Checker(res.get, setattr_permission_func)       

         time_service_checker = PermissionMapChecker(
                                        # permission : [methods]
                                        {'AccessTimeService':['getTime']}
                                        )

      with the NoSetAttr function defined as a lambda which always
      return the permission NotAllowed

      To bind the checkers to the simulation classes we register
      our checkers with the security model's global checker registry::
      
         import sandbox_simulation
         from Zope.Security.Checker import defineChecker
         defineChecker(sandbox_simulation.TimeService, time_service_checker)

    Defining a Security Policy
             
      we implement our security policy such that it checks the
      current agent's authentication token against the given 
      permission against the home of the object being accessed.

      in code::             

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

      there is some additional code present to allow for shortcuts
      in defining the permission database when defining permissions
      for all auth groups and all permissions.

    Integration

      At this point we have implemented our security model, and 
      we need to integrate it with our simulation model. we do so
      in three separate steps. 

      first we make it such that agents only access homes that are 
      wrapped in a security proxy. by doing this all access to homes 
      and services (proxies have proxied return values for their 
      methods) is implicitly guarded by our security policy.

      the second step is that we want to associate the active agent
      with the security context so the security policy will know
      which agent's authentication token to validate against.

      the third step is to set our security policy as the default
      policy for the zope security framework. it is possible to 
      create custom security policies at a finer grained than global,
      but such is left as an exercise for the reader.

    Security Manager Access

      The *default* implementation of the security management interfaces
      defines security managers on a per thread basis with a function
      for an accessor, this model is not appropriate for all systems,   
      as it restricts one to a single active user per thread at any
      given moment, reimplementing the manager access methods though
      is easily doable and is noted here for completeness.

    Perspectives

      Its important to keep in mind that there is alot more that
      is possible using the security framework thans what been
      presented here. all of the interactions are interfaced based,
      such that if you need to reimplement the semantics to suite
      your application a new implementation of the interface will be
      sufficient. Additional possiblities range from restricted 
      interpreters and dynamic loading of untrusted code to non zope
      web application security systems.. insert imagination here ;-).

    Zope Perspective

      A Zope3 programmer will never commonly need to interact with the
      low level security framework. Zope3 defines a second security
      package overtop the low level framework that implements concepts
      of roles and authentication sources and checkers are handled via
      zcml registration. Still those developing Zope3, will hopefully
      find this useful as an introduction into the underpinnings of
      the security framework.

    Code

      The complete code for this example is available.

      sandbox.py - the agent framework

      sandbox_security.py - the security implementation and binding to
      the agent framework.
             
    Author

      Kapil Thangavelu <hazmat at objectrealms.net>
      
      Guido Wesdorp <guido at infrae.com>
     
