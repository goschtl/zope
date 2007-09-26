from zope.app import zapi
from zope.dublincore.interfaces import ICMFDublinCore

class EntryDetails:

    def author(self):
        """Get user who last modified the Message."""
        creators = ICMFDublinCore(self.context).creators
        if not creators:
            return 'unknown'
        return creators[0]

    def description(self):
        """Get description of Entry"""
        return ICMFDublinCore(self.context).description

    def modified(self):
        """Get last modification date."""
        date = ICMFDublinCore(self.context).modified or \
               ICMFDublinCore(self.context).created or ''
        return date.strftime('%FT%TZ')

    def title(self):
        """Get title of Entry"""
        return ICMFDublinCore(self.context).title
