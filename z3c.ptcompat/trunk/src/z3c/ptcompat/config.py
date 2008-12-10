import os
import logging
import z3c.ptcompat

PREFER_Z3C_PT = os.environ.get("PREFER_Z3C_PT", 'false').lower() in \
                ('y', 'yes', 't', 'true', 'on', '1')

if PREFER_Z3C_PT:
    try:
        import z3c.pt
    except ImportError:
        logging.getLogger('z3c.ptcompat').warn(
            "Unable to import ``z3c.pt``.")
        PREFER_Z3C_PT = False    

def enable():
    global PREFER_Z3C_PT
    PREFER_Z3C_PT = True
    reload(z3c.ptcompat)

def disable():
    global PREFER_Z3C_PT
    PREFER_Z3C_PT = False
    reload(z3c.ptcompat)
    
