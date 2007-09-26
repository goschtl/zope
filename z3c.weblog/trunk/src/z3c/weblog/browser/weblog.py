from zope.app import zapi
from zope.dublincore.interfaces import ICMFDublinCore
from zope.app.container.interfaces import IContentContainer

class WeblogView:

    def description(self):
        """Get description of Entry"""
        return ICMFDublinCore(self.context).description

    def modified(self):
        """Get last modification date."""
        date = ICMFDublinCore(self.context).modified or \
               ICMFDublinCore(self.context).created or ''
        return date.strftime('%FT%TZ')

    def author(self):
        """Get the Author of the weblog"""
        # What we actually want is the author, but for now we'll use the creator
        creators = ICMFDublinCore(self.context).creators
        if not creators:
            return 'unknown'
        return creators[0]

    def title(self):
        """Get title of Entry"""
        return ICMFDublinCore(self.context).title

    def getEntryData(self):
        """Get the contained object's data"""
        entries = []
        for entry in IContentContainer(self.context).values():
            date = ICMFDublinCore(entry).modified or \
                   ICMFDublinCore(entry).created or ''
            d = dict(
                title = ICMFDublinCore(entry).title,
                modified = date.strftime('%FT%TZ'),
                link = zapi.absoluteURL(entry, self.request),
                description = ICMFDublinCore(entry).description,
                )
            entries.append(d)
        return entries

