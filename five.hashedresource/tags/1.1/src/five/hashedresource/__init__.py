import Globals
import sys


# Communicate to ZCML whether debug-mode is on. As ZCML conditions have only
# two verbs currently ('have' and 'installed') and it doesn't seem to be
# possible to switch features on and off programmatically, we make a dummy
# module importable or not depending on debug-mode so ZCML can ask about it
# using the 'installed' verb.

if not getattr(Globals, 'DevelopmentMode', False):
    sys.modules['five.hashedresource.__debug_mode__'] = None
