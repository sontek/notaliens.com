def includeme(config):

    config.override_asset(
        to_override='horus:templates/edit_profile.mako'
        , override_with='notaliens:people/templates/edit_profile.mako'
    )

    config.include('notaliens.people.routes')
