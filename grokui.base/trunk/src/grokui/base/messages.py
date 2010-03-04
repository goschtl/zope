# -*- coding: utf-8 -*-

import grok
from grokcore.message import UniqueMessageSource

class AdminMessageSource(UniqueMessageSource):
    """Source for the administration messages
    """
    grok.name('admin')
