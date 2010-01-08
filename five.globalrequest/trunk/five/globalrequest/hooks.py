from zope.globalrequest import setRequest, clearRequest

def set(event):
    setRequest(event.object)

def clear(event):
    clearRequest()
