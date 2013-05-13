def includeme(config):
    config.include('notaliens.core.routes')

    config.include('notaliens.people', route_prefix='/people')
