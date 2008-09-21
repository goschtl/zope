from datetime import datetime

import grok

class Paste(grok.Model):

    def __init__(self, author_name='', paste='', language=''):
        super(Paste, self).__init__()
        self.author_name = author_name
        self.paste = paste
        self.language = language
        self.date = datetime.now()
        
    def to_dict(self):
        return {'pasteid': self.pasteid,
                'author_name': self.author_name,
                'language': self.language,
                'paste': self.paste,
                'date': str(self.date),
                }


