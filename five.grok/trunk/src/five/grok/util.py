from martian.error import GrokError

from martian.util import class_annotation

def get_default_permission(factory):
    """Determine the default permission for a view.

    There can be only 0 or 1 default permission.
    """
    permissions = class_annotation(factory, 'grok.require', [])
    if not permissions:
        return 'zope.Public'
    if len(permissions) > 1:
        raise GrokError('grok.require was called multiple times in '
                        '%r. It may only be set once for a class.'
                        % factory, factory)

    result = permissions[0]
    return result
