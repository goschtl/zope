# -*- coding: utf-8 -*-
"""This module can be grokked if you need a generic flash message setup.
"""
import grokcore.component
import z3c.flashmessage.sources
import z3c.flashmessage.receiver


grokcore.component.global_utility(
    z3c.flashmessage.sources.SessionMessageSource, name='session')

grokcore.component.global_utility(
    z3c.flashmessage.receiver.GlobalMessageReceiver)
