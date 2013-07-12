from pyramid.view import view_config

@view_config(
    route_name='jobs_index',
    renderer='notaliens:jobs/templates/index.mako'
)
def sites_index(request):
    return {}
