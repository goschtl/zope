from z3c.traverser.stackinfo import traversing

# example event handler
def handleSiteBeforeTraverse(obj, event):
    traversing.applyStackConsumers(obj, event.request)
    
