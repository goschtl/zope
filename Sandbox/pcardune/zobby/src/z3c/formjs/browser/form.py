class FormScripts(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context
        
    def __call__(self):
        return """
    <script type=\"text/javascript\" src=\"/@@/jsolait/jsolait.js\"></script>
    <script type=\"text/javascript\" src=\"/@@/z3c.javascript.jquery/jquery.js\"></script>
    <script type=\"text/javascript\" src=\"++resource++z3c.formjs/formjs.js\"></script>
        """
