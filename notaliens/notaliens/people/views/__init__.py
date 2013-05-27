from pyramid.view import view_config
from notaliens.identity.models import get_user_by_username

@view_config(
    route_name='people_index'
    , renderer='notaliens:people/templates/index.mako'
)
def people_index(request):
    return {}

@view_config(
    route_name='people_profile'
    , renderer='notaliens:people/templates/profile.mako'
)
def people_profile_view(request):
    user = get_user_by_username(
        request.db_session,
        request.matchdict['user_name']
    )

    return {
        'user': user
    }
