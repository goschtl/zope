from zope.interface import Interface
from zope.configuration.fields import Tokens, GlobalObject


class IReloadDirective(Interface):

    classes = Tokens(
        title=u"View classes",
        required=False,
        value_type=GlobalObject(
                title=u"View class",
                description=u"""
                A view class for which automatic reload should be enabled.
                """))

    modules = Tokens(
        title=u"Modules",
        required=False,
        value_type=GlobalObject(
                title=u"Module",
                description=u"""
                A module containing views for which automatic reload should be
                enabled.
                """))

    packages = Tokens(
        title=u"Packages",
        required=False,
        value_type=GlobalObject(
            title=u"Package",
            description=u"""
            A package containing views for which automatic reload should be
            enabled.

            `module` only works for a single module, whereas `package` also
            applies for contained modules and packages.
            """))


# TODO: reload:omit, reload:all
