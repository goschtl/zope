from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer

class RenderReST:
    """Provide an interface for viewing a Proposal as ReST"""
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.title = context.title
        self.usecase = self.render(context.usecase)
        self.concept = self.render(context.concept)
        self.todo = self.render(context.todo)
        self.issues = self.render(context.issues)

    def render(self,content):    
        """render contextattributes to ReST"""
        if content:
            html = ReStructuredTextToHTMLRenderer(content.encode('utf-8'),
                                              self.request)
            return unicode(html.render(),'utf-8')