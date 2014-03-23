from notaliens.scripts import (
    geoip, geoip_csv, reindex, create, refresh_user_location
)
from notaliens.tasks import worker

import argparse
import sys


class NotAliensCommand(object):

    prog = 'notaliens'
    description = ''
    parse = argparse.ArgumentParser(prog=prog, description=description)

    parse.add_argument('--init', dest='init', help='prepare your environment',
            action='count')
    parse.add_argument('--geoip', dest='geoip', help='download geoip database',
            action='count')
    parse.add_argument('--geoip-csv', dest='geoip_csv',
                       help='update geoip database from csv file',
                       action='count'
                       )
    parse.add_argument('--reindex', dest='reindex',
                       help='reindex database and elasticsearch',
                       action='count'
                       )
    parse.add_argument('--refresh-location', dest='location',
                       help='refresh user location',
                       action='count'
                       )
    parse.add_argument('--task-queue',
                       help='running the task queue worker',
                       action='count'
                       )


    def __init__(self, argv):
        self.option = self.parse.parse_args(argv[1:])
        self.config_file = 'development.ini'

    def run(self):
        if self.option.init:
            return self.initialize()
        elif self.option.geoip:
            return self.geoip()
        elif self.option.geoip_csv:
            return self.geoip_csv()
        elif self.option.reindex:
            return self.reindex()
        elif self.option.location:
            return self.refresh_user_location()
        elif self.option.task_queue:
            return self.worker()

    def createdb(self):
        return create.main(self.config_file)

    def geoip(self):
        return geoip.update(self.config_file)

    def geoip_csv(self):
        return geoip_csv.update(self.config_file)

    def reindex(self):
        return reindex.main(self.config_file)

    def location(self):
        return refresh_user_location.update(self.config_file)

    def task_queue(self):
        return worker.main(self.config_file)

    def initialize(self):
        """Running createdb, geoip and reindex"""
        
        self.createdb()
        self.geoip()
        self.reindex()


def main(argv=sys.argv):
    command = NotAliensCommand(argv)
    return command.run()

if __name__ == '__main__':
    sys.exit(main() or 0)
