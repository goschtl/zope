from zope.interface import Interface,Attribute
from zope.schema import Text, TextLine, Field, Choice
from zope.app.container.constraints import ContainerTypesConstraint, ItemTypePrecondition
from zope.app.container.constraints import contains, containers
from zope.app.container.interfaces import IContainer, IContained

class IOrganization(Interface):
    """An Organization object. This contains projects, mentors and students"""

    name=TextLine(
        title=u"Organization Name",
        description=u"Name of the organization",
        default=u"",
        required=True)

class IGsoc(IContainer):
    """This is the root object of this project. It can only contain IOrganization objects"""

    contains(".IOrganization")

    description = Text(
        title=u"Description",
        description=u"A detailed description about the content on the Gsoc",
        default=u"",
        required=False)

class IProject(Interface):
    """A Project object."""

    name = TextLine(title=u"Project Name")

    description = TextLine(title=u"Project Description")


class IStudent(Interface):
    """A Student object"""

    name = TextLine(title=u"Student Name")


class IMentor(Interface):
    """A Mentor object"""

    name = TextLine(title=u"Mentor Name")

    #project=Choice(
    #    title=u"Prefered project",
    #    vocabulary=u"vocab_of_IProject",
    #    required=False)

class IOrganizationContained(IContained):
    """Interface that specifies type of objects that can contain in an organization"""

    containers(".IGsoc")


class IOrganizationContainer(IContainer):
    """Organization is also a container for projects, students and mentors"""

    contains(".IProject", ".IStudent", ".IMentor")
    
class IProjectRelation(Interface):
    mentor = Attribute('assigned mentor for the project')
    project = Attribute('mentoring project')
    
    