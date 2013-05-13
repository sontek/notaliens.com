def includeme(config):
    config.include('notaliens.identity.routes')

    config.include('horus')
    config.scan_horus('notaliens.identity.models')
