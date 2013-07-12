from pyramid.view import view_config

@view_config(
    route_name='sites_index',
    renderer='notaliens:sites/templates/index.mako'
)
def sites_index(request):
    return {}
