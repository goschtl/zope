# -*- coding: UTF-8 -*-
from zope.interface import implements
from zope.interface import Interface
import persistent

from ocql.testing.sample.interfaces import IProject, IProjectRelation

class Project(persistent.Persistent):
    """A simple implementation of a Project .

    Make sure that the ``Project`` implements the ``IProject`` interface:


    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IProject, Project)
    True

    Here is an example of changing the name of the project:

    >>> project = Project()
    >>> project.name
    u''

    >>> project.name = u'Project Name'
    >>> project.name
    u'Project Name'
    """
    implements(IProject)

    # See google.interfaces.IProject
    name = u''

    def __repr__(self):
        return "%s <%s>" % (self.__class__.__name__, self.name)


class ProjectRelation(object):
    implements(IProjectRelation)
    
    def __init__(self, mentor, project):
        self.mentor = mentor
        self.project = project
