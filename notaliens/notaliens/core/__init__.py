from sqlalchemy import engine_from_config
from hem.interfaces import IDBSession
from notaliens.core.interfaces import IDBSessionMaker
from notaliens.core.models import DBSession

def get_db_session(request):
    """
    This will be lazily loaded whenever the `db_session` attribute
    is accessed on the request.  It will create the SQLAlchemy session
    and attach a finish callback on the request that will close the
    session
    """

    session = request.registry.getUtility(IDBSessionMaker)

    def cleanup(request):
        session.close()

    # This makes sure at the end of the request, we always close our
    # database connection
    request.add_finished_callback(cleanup)

    return session

def includeme(config):

    engine = engine_from_config(
        config.registry.settings, prefix='sqlalchemy.'
    )

    DBSession.configure(bind=engine)

    config.registry.registerUtility(DBSession, IDBSessionMaker)

    # primarily used for horus
    config.registry.registerUtility(get_db_session, IDBSession)

    config.add_request_method(get_db_session, 'db_session', reify=True)

    config.include('notaliens.core.routes')
