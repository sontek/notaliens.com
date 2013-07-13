import logging
from .phantomjs import take_screenshot

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
        take_screenshot(task_data)

