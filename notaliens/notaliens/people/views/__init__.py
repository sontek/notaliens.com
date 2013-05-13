from pyramid.view import view_config

@view_config(
    route_name='people_index'
    , renderer='notaliens:people/templates/index.mako'
)
def people_index(request):
    return {}
