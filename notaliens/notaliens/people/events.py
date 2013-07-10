def display_name(user):
    first = user['profile']['first_name']
    last = user['profile']['last_name']

    if first and last:
        return '%s %s' % (first, last)
    elif first and not last:
        return first
    else:
        return user['username']


def add_renderers(event):
    event['display_name'] = display_name
