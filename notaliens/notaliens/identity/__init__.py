from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

def includeme(config):
    authentication_policy = AuthTktAuthenticationPolicy(
        config.registry.settings['auth.secret']
    )

    authorization_policy = ACLAuthorizationPolicy()

    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)

    config.include('notaliens.identity.routes')

    config.include('horus')

    config.override_asset(
        to_override='horus:templates/'
        , override_with='notaliens:identity/templates/'
    )

    config.scan_horus('notaliens.identity.models')
