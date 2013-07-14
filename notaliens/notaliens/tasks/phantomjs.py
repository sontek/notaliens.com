from subprocess import call

def take_screenshot(data):
    folder = data['folder']
    pjs = data['pjs']
    script = data['script']
    url = data['url']
    pk = data['pk']

    path = '%s/site_%s.png' % (folder, pk)
    call([pjs, script, url, path])

    return path

