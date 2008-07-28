========================
Hierarchial roles
========================

Hierarchical roles are roles that can include other roles. This way,
hierarchical roles can be created. For instance, one can think of
the following roles:

1) Visitor (An anonymous role)
2) Registered (Registered Users)
3) Admin (The Administrator)

In this example, the registered user should have the same permissions
as the visitor, and the admin should have the same as the registered user
and some extra permissions.

In ZCML, this can be handled like this:

<permission 
    id="p1"
    title="Look at a page"
/>

<permission 
    id="p2"
    title="Edit a page"
/>

<permission 
    id="p3"
    title="Administer Users"
/>

<hrole
    id="test.Visitor"
    title="Anonymous Visitor"
/>

<hrole
    id="test.Registered"
    title="Registered User"
    includes = "test.Visitor"
/>

<hrole
    id="test.Admin"
    title="Administrator"
    includes = "test.Registered"
/>

<grant
    permission="p1"
    role="test.Visitor"
/>

<grant
    permission="p2"
    role="test.Registered"
/>

<grant
    permission="p3"
    role="test.Admin"
/>

The Administrator will now have permission p1, p2 and p3. It is also
possible to include multiple permissions:

<hrole    
    id="test.Admin"
    title="Administrator"
    includes = "test.Visitor, test.Registered"
/>

