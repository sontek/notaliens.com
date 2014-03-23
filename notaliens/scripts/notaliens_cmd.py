import argparse


class NotAliensCommand(object):

    prog = 'notaliens'
    description = ''
    parse = argparse.ArgumentParser(prog=prog, description=description)

    parse.add_argument('--init', dest='init', help='prepare your environment')
    parse.add_argument('--geoip', dest='geoip', help='download geoip database')
    parse.add_argument('--geoip-csv', dest='geoip_csv',
                       help='update geoip database from csv file'
                       )
    parse.add_argument('--reindex', dest='redinex',
                       help='reindex database and elasticsearch'
                       )
