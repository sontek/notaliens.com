from hem.interfaces import IDBSession
from notaliens.core.models import DBSession

def includeme(config):
    config.include('notaliens.identity.routes')

    # Tell horus which SQLAlchemy session to use:
    config.registry.registerUtility(DBSession, IDBSession)

    config.include('horus')

    #config.override_asset(
    #    to_override='horus:templates/'
    #    , override_with='notaliens:identity/templates/'
    #)

    config.scan_horus('notaliens.identity.models')
