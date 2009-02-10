


class IBrowserRequest(IHTTPRequest):
    """Browser-specific Request functionality.

    Note that the browser is special in many ways, since it exposes
    the Request object to the end-developer.
    """

class IBrowserSkinType(IInterface):
    """A skin is a set of layers."""

class IDefaultSkin(Interface):
    """Any component providing this interface must be a skin.

    This is a marker interface, so that we can register the default skin as an
    adapter from the presentation type to `IDefaultSkin`.
    """

class ISkinChangedEvent(Interface):
    """Event that gets triggered when the skin of a request is changed."""

    request = Attribute("The request for which the skin was changed.")
