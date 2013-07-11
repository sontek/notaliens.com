def display_name(user):
    first = user['profile']['first_name']
    last = user['profile']['last_name']

    if first and last:
        return '%s %s' % (first, last)
    elif first and not last:
        return first
    else:
        return user['username']

def display_location(user):
    city = user['profile']['city']
    state = user['profile']['state']
    country = user['profile']['country']

    nodes = []
    if city:
        nodes.append(city)

    if state:
        nodes.append(state)

    if country:
        nodes.append(country['alpha2'])

    return ', '.join(nodes)


def add_renderers(event):
    event['display_name'] = display_name
    event['display_location'] = display_location
