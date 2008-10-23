from zope import interface

class IForm(interface.Interface):
    """Base form class. Optionally pass a dictionary as ``data`` and a
    WebOb-like request object as ``request``. A ``context`` may be
    provided instead of ``data``."""
