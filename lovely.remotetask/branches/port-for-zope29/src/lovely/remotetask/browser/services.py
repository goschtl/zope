class Add(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        name = self.request.get('name')
        if not name:
            return "name wasn't supplied"
