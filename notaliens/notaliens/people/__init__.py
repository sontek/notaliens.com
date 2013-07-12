from pyramid.events import BeforeRender
from horus.interfaces import IProfileSchema
from horus.events import ProfileUpdatedEvent

from notaliens.people.schemas import ProfileSchema
from notaliens.people.views import handle_profile_update


def includeme(config):
    config.override_asset(
        to_override='horus:templates/edit_profile.mako',
        override_with='notaliens:people/templates/edit_profile.mako'
    )

    config.registry.registerUtility(ProfileSchema, IProfileSchema)

    config.include('notaliens.people.routes')

    config.add_subscriber(
        'notaliens.people.events.add_renderers',
        BeforeRender
    )

    config.add_subscriber(handle_profile_update, ProfileUpdatedEvent)
