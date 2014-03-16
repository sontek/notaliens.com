from notaliens.people.security import UserFactory


def includeme(config):
    config.add_route('people_index', '/')
    config.add_route('people_index_paged', '/page/{page}')
    config.add_route('people_profile', '/user/{username}')

    config.add_route(
        'people_edit_profile',
        '/{username}/edit',
        factory=UserFactory,
        traverse='/{username}'
    )

    # override horus
    config.add_view(
        'horus.views.ProfileController',
        attr='edit_profile',
        route_name='people_edit_profile',
        permission='access_user',
        renderer='notaliens:people/templates/edit_profile.mako'
    )
