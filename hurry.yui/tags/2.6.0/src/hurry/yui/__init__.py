try:
    from hurry.yui.yui import *
except ImportError:
    # nasty to ignore this, but can't self-prepare library if no yui.py is
    # there yet
    pass

