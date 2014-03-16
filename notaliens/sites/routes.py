from notaliens.sites.security import SiteFactory

def includeme(config):
    config.add_route('sites_index', '/')
    config.add_route('sites_index_paged', '/page/{page}')
    config.add_route('sites_details', '/details/{site_pk}')
    config.add_route('sites_new', '/new')
    config.add_route(
        'sites_edit_details',
        '/{site_pk}/edit',
        factory=SiteFactory,
        traverse='/{site_pk}'
    )
    config.add_static_view(name='screenshots', path='notaliens:static/screenshots')
