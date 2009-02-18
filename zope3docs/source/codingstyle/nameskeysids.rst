Names, Keys and Ids

Author

  "Steve Alexander":mailto:steve@cat-box.net

Obligatory quotation::

  Everybody has a name, but names are only words

                          "I'm not built for this"
                                The Nilon Bombers

Problem

  Sometimes we say 'key', sometimes 'name', and sometimes 'id'. This
  could get confusing, and we should try to be consistent. Here's a 
  summary of how these terms are used.
  
  Key
  
    The IContainerPythonification proposal has been implemented, and
    components that are containers have methods to get at contained
    objects that look like '__getitem__(key)', 'get(key, default=None)',
    and 'setObject(key, object)'.

  Name
  
    We also have the notion that objects have names. For example the
    code below will give the name we used to traverse from someObject's
    container to 'someObject'::

      from Zope.App.Traversing import objectName
      print "someObject's name is ", objectName(someObject)

    There's also a view that works similarly to the 'absolute_url' view
    called 'object_name'. This can be used in Page Templates::

      <h3>Job #<span tal:replace="context/@@object_name">NN</span></h3>

    In this example, '@@object_name' gets you the 'object_name' view, which
    gets the same result as 'getAdapter(someObject, IObjectName)()'.
  
    Various documentation talks about "named objects". We talk informally 
    about Services being identified by "name", even though they are really
    identified by an id.
    
  Id

    In Zope 2, content objects have a method 'getId()', and containers 
    have methods 'objectIds()', '_setId()', and so on.
    

Proposal

  This is my explanation, or rationalisation, of when to use the terms 'id', 
  'name', and 'key'.

  Id

    The term 'id' should only be used when we are talking about an identifier
    that is unique in the context of some particular id scheme. Examples include

    * A social security number, unique within a country's social secuity 
      bureaucracy

    * A user id consisting of an NT Domain and a username, unique within
      a Windows NT network

    * A user id, unique within a Windows NT Domain

    * A Windows NT domain, unique within a Windows network

    We could consider the name of an object within a container to be an id within
    the id scheme of that container, but this is not a particularly useful
    way of thinking. One reason is that to identify the container, we need to
    consider it as having an id within the id scheme of *its* container.

    Id schemes should really be well-known points of reference within a system.
    So, the model of Services in Zope 3 fits; you look up a service by its
    id within the service manager id scheme.
  
  Name
  
    Objects are given names to help us find them. An object may be found
    via more than one name. In Zope 3, we use names to guide the process
    of traversing from a container to a contained object.
    
  Key
  
    We use an object's name to get it from within a container.
    The container sees these names as 'keys', so from a container's point
    of view, a name functions as a key to look up an object.
    
    When we use the term 'key', we really mean "a name functioning as a
    key in the context of a container".
    
    
References

  Martin Fowler, "Analysis Patterns: reusable object models", Addison Wesley
  1997. Chapter 5 "Referring to Objects" has a good discussion of names, ids
  and id schemes.
  


<hr solid id=comments_below>


bwarsaw (Jun 17, 2002 9:27 am; Comment #1)  --
 We also have *message ids* which are unique identifiers for translatable messages within a particular application/product domain.
 
