def includeme(config):
    config.add_route('people_index', '/')
    config.add_route('people_profile', '/{user_name}')
