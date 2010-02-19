from zope.interface import Interface
from zope.schema import Choice, List


class IReload(Interface):
    """Interface for the ZCML reload view.
    """

    applications = List(
        title = u"Application",
        description=u"Pleas select a Application which should be reloaded",
        value_type=Choice(vocabulary="megrok.reload.applications")
        )
        

    def status():
        """Return a status text."""

    def code_reload():
        """Reload all changed code."""

    def zcml_reload():
        """Reprocess all global ZCML."""
