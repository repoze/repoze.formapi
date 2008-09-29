from zope import interface

import interfaces

class Form(object):
    interface.implements(interfaces.IForm)
    
    def __init__(self, model, context=None, prefix=None):
        self.model = model
        self.context = context
        self.prefix = prefix

    def validate(self, request):
        return self.model(request).validate_form()
        
