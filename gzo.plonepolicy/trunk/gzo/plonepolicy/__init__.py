#
# ReST features that are not included in Plone 3.0.x that we are using
#
# See rest_extensions/README.txt for further infos.
#
from rest_extensions import directives_plain, roles_plain, pygments_directive

def initialize(context):
    """Intializer called when used as a Zope 2 product."""
