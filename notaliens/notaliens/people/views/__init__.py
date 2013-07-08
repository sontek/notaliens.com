from pyramid.view import view_config
from notaliens.people.models import get_user_by_username
from notaliens.people.models import get_users

@view_config(
    route_name='people_index'
    , renderer='notaliens:people/templates/index.mako'
)
@view_config(
    route_name='people_index_paged'
    , renderer='notaliens:people/templates/index.mako'
)
def people_index(request):
    page = request.matchdict.get('page', 0)

    return {
        'data': get_users(request, page=page)
    }

@view_config(
    route_name='people_profile'
    , renderer='notaliens:people/templates/profile.mako'
)
def people_profile_view(request):
    user = get_user_by_username(
        request.db_session,
        request.matchdict['username']
    )

    return {
        'user': user
    }
