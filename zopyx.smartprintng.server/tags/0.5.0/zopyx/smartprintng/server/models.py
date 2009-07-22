##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


class Server(object):
    pass

root = Server()

def get_root(environ):
    return root
