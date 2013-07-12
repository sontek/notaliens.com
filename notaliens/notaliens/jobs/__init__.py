from pyramid.events import BeforeRender

JOB_INDEX = 'jobs'


def includeme(config):
    config.include('notaliens.jobs.routes')

    config.add_subscriber(
        'notaliens.jobs.events.add_renderers',
        BeforeRender
    )
