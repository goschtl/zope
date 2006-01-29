from zope.app.contenttypes import text_type, guess_content_type, add_files
from zope.deprecation import deprecated

msg = ('zope.app.content_types has moved to zope.app.contenttypes. '
       'This reference go away in Zope 3.4.')

deprecated('text_type', msg)
deprecated('guess_content_type', msg)
deprecated('add_files', msg)
