import hashlib

try:
    from urllib.parse import urlencode  # Python 3
except ImportError:
    from urllib import urlencode  # Python 2


def gravatar_url(email, size=80, default='mm', cacheable=True):
    base = "http://www.gravatar.com/avatar/" if cacheable else \
        "https://secure.gravatar.com/avatar/"
    return base + \
        hashlib.md5(email.encode('utf8').lower()).hexdigest() + \
        "?" + urlencode({'d': default, 's': str(size)})

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
    country = None

    if 'country' in user['profile']:
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
    event['gravatar_url'] = gravatar_url
