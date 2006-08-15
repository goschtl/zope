from zope import interface
import zope.component.interfaces

class VersionedError(Exception):
    """The object is already versioned and cannot be changed."""

class VersioningError(Exception):
    """The object is unable to be versioned at this time."""

class IObjectVersionedEvent(zope.component.interfaces.IObjectEvent):
    """The object is being versioned"""

class ObjectVersionedEvent(zope.component.interfaces.ObjectEvent):
    """Object was versioned"""

    interface.implements(IObjectVersionedEvent)

class IVersionable(interface.Interface):
    """Marker interface specifying that it is desirable to adapt the object to
    IVersioning"""

class IVersioning(IVersionable):
    _z_versioned = interface.Attribute(
        """Boolean, whether the object is versioned.  Readonly""")

    _z_version_timestamp = interface.Attribute(
        "datetime.datetime in pytz.utc of when versioned, or None.  Readonly.")

    def _z_version():
        """sets _z_versioned to True and fires ObjectVersioned event.
        raises VersionedError if _z_versioned is already True."""

class ResumeCopy(Exception):
    """do not use the hook: continue copying recursively
    (see ICopyHook.__call__)"""

class ICopyHook(interface.Interface):
    """an adapter to an object that is being copied"""
    def __call__(location, register):
        """Given the top-level location that is being copied, return the
        version of the adapted object that should be used in the new copy.

        raising ResumeCopy means that you are foregoing the hook: the
        adapted object will continue to be recursively copied.

        If you need to have a post-creation cleanup, register a callable with
        `register`.  This callable must take a single argument: a callable that,
        given an object from the original, returns the equivalent in the copy.
        """

class IVersioningData(interface.Interface):
    """An object used to store version data for another object.  Useful for
    the copy hook.  Only of internal interest."""

    _z_version_timestamp = interface.Attribute(
        "datetime.datetime in pytz.utc of when versioned, or None.")