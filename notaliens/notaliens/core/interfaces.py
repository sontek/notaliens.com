from zope.interface import Interface


class IDBSessionMaker(Interface):
    """ Marker interface for registering a db session maker
    """
    pass
