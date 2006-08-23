from zope import interface

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
