from zope.globalrequest import setRequest, clearRequest

def set(event):
    setRequest(event.request)

def clear(event):
    clearRequest()
