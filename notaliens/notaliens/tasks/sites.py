import logging
from .phantomjs import take_screenshot
from PIL import Image

log = logging.getLogger(__name__)

class CaptureScreenshot(object):
    queue = 'screenshots'

    @classmethod
    def enqueue(cls, request, site):
        """
        Build the task data and enqueue the phantonjs take_screenshot
        task for the given site.
        """
        task_data = {
            'folder':request.registry['screenshots_folder'],
            'pjs':request.registry['phantomjs_path'],
            'script':request.registry['phantomjs_script'],
            'pk':site.pk,
            'url':site.url,
        }
        request.resq.enqueue(cls, task_data)
        log.info('Queued screenshot capture for Site(pk=%s)' % site.pk)

    @staticmethod
    def perform(task_data):
        log.info('Performing screenshot capture for Site(pk=%s)' % task_data['pk'])
        image_path = take_screenshot(task_data)
        generate_thumbnail(task_data, image_path, (400,400))

def generate_thumbnail(data, image_path, size):
    image = Image.open(image_path)
    thumbnail = image.copy()
    thumbnail_path = '%s/site_%s.thumbnail.png' % (data['folder'], data['pk'])

    def grow(size, color=(255,255,255,0)):
        n_x, n_y = size
        x, y = thumbnail.size

        centered = ((n_x - x) / 2, (n_y - y) / 2)
        box = Image.new('RGBA', size, color)
        box.paste(thumbnail, centered)
        box.save(thumbnail_path)

    def scale(size):
        thumbnail.thumbnail(size, Image.ANTIALIAS)
        thumbnail.save(thumbnail_path)

    n_x, n_y = size
    x, y = thumbnail.size

    if x > n_x or y > n_y:
       scale(size)

    x, y = thumbnail.size
    if x < n_x or y < n_y:
       grow(size)

