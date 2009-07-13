import Products.Five.browser.metaconfigure
import zope.publisher.interfaces.browser
import five.hashedresource.url
import z3c.hashedresource.hash
import zope.component.zcml
import zope.traversing.browser.interfaces
from zope.publisher.interfaces.browser import IBrowserRequest



def hashedResourceDirectory(
        _context, name, directory,
        layer=zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        permission='zope.Public'):
    already_registered = len(_context.actions)
    Products.Five.browser.metaconfigure.resourceDirectory(
        _context, name, directory, layer, permission)
    new_classes =[r[0][1] for r in _context.actions[already_registered:]
        if isinstance(r[0], tuple) and r[0][0] ==  'five:initialize:class']
    for new_class in new_classes:
        _context.action(
            discriminator = ('adapter',
                             (new_class, IBrowserRequest),
                             zope.traversing.browser.interfaces.IAbsoluteURL,
                             ''),
            callable = zope.component.zcml.handler,
            args = ('registerAdapter',
                    five.hashedresource.url.HashingURL,
                    (new_class, IBrowserRequest),
                    zope.traversing.browser.interfaces.IAbsoluteURL,
                    '',
                    _context.info),
        )
        _context.action(
            discriminator = ('adapter',
                             new_class,
                             z3c.hashedresource.interfaces.IResourceContentsHash,
                             ''),
            callable = zope.component.zcml.handler,
            args = ('registerAdapter',
                    z3c.hashedresource.hash.ContentsHash,
                    (new_class,),
                    z3c.hashedresource.interfaces.IResourceContentsHash,
                    '',
                    _context.info),
        )
