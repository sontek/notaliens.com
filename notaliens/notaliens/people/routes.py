from notaliens.people.security import UserFactory

def includeme(config):
    config.add_route('people_index', '/')
    config.add_route('people_profile', '/{user_name}')


    config.add_route(
        'people_edit_profile'
        , '/{user_name}/edit'
        , factory=UserFactory
        , traverse='/{user_name}'
    )

    # override horus
    config.add_view(
        'horus.views.ProfileController'
        , attr='edit_profile'
        , route_name='people_edit_profile'
        , permission='access_user'
        , renderer='notaliens:people/templates/edit_profile.mako'
    )
