class Request:
    application_url = 'http://app'
    def __init__(self, environ=None, params=None):
        if environ is None:
            environ = {}
        self.environ = environ
        if params is None:
            params = {}
        self.params = params
