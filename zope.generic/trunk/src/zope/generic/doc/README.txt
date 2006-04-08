============
zope.generic
============

Software models problem domains. Often we model domain components as object
of corresponding implementations (classes). Those classes combine generic 
behavior and domain-specific behavior. This packages should help to model problem
domains using generic implementations that do not provide any domain-specific 
behavior directly but mark instances of those generic implementations 
domain-specifically relying heavily on the directly provide mechanism of the
zope.interface package.

-   .directlyprovides: Better control of the directly provides mechanism

-   .configuration: n/a

-   .information: Interface-based registrations and registries

-   .type: Type generic base classes by marker interfaces.

