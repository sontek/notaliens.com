def includeme(config):
    config.include('notaliens.identity.routes')

    config.include('horus')

    config.override_asset(
        to_override='horus:templates/'
        , override_with='notaliens:identity/templates/'
    )

    config.scan_horus('notaliens.identity.models')
