import os
import sys
import pytz
import pycountry

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from sqlalchemy import engine_from_config
from getpass import getpass

from pyramid.paster import (
    bootstrap
    , setup_logging
)

from pyramid.config import Configurator

from notaliens.core.models import Base
from notaliens import setup_includes

try: 
    input = raw_input
except NameError:
    pass

here = os.path.dirname(__file__)

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)


def setup_global_data(session):
    """ This is used to setup global like timezones, countries,
    and languages
    """
    from notaliens.core.models.meta import Timezone
    from notaliens.core.models.meta import Country
    from notaliens.core.models.meta import Currency
    from notaliens.core.models.meta import Language

    timezones = []

    for timezone in pytz.common_timezones:
        new_timezone = Timezone(name=timezone)
        timezones.append(new_timezone)
        session.add(new_timezone)

    countries = []

    for country in pycountry.countries:
        new_country = Country(
                name=country.name,
                alpha2=country.alpha2,
                alpha3=country.alpha3,
                numeric=country.numeric
        )

        if hasattr(country, 'official_name'):
            new_country.official_name = country.official_name

        countries.append(countries)
        session.add(new_country)

    currencies = []

    for currency in pycountry.currencies.objects:
        new_currency = Currency(name=currency.name, letter=currency.letter)
        currencies.append(new_currency)
        session.add(new_currency)

    lang_blacklist = [
        "English, Old (ca.450-1100)"
        , "English, Middle (1100-1500)"
        , "German, Middle High (ca.1050-1500)"
        , "German, Old High (ca.750-1050)"
        , "Irish, Middle (900-1200)"
        , "Irish, Old (to 900)"
        , "Persian, Old (ca.600-400 B.C.)"

    ]

    lang_convert_list = {
        "Spanish; Castilian": "Spanish"
    }

    languages = []

    with open(os.path.join(here, 'ISO-639-languages.txt')) as f:
        lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line:
                values = [x.strip() for x in line.split('|')]
                name = values[3]

                # breakout if its in our blacklist
                if name in lang_blacklist:
                    continue

                if name in lang_convert_list:
                    name = lang_convert_list[name]

                language = Language(
                    alpha3_bib=values[0]
                    , alpha3_term=values[1]
                    , alpha2=values[2]
                    , name=name
                )

                session.add(language)

        return {
            'currencies': currencies
            , 'timezones': timezones
            , 'countries': countries
            , 'languages': languages
        }


def generate_default_data(session):
    from notaliens.identity.models import User
    from notaliens.people.models import UserProfile

    global_data = setup_global_data(session)

    username = input("What is your username?: ")
    email = input("What is your email?: ")
    password = getpass("What is your password?: ")
    first_name = input("What is your first name?: ")
    last_name = input("What is your last name?: ")
    one_liner = input("Please provide a 140 char description: ")


    admin = User(
        username=username
        , email=email
        , password=password
    )

    profile = UserProfile(
        user=admin
        , first_name=first_name
        , last_name=last_name
        , one_liner=one_liner
    )

    global_data['profiles'] = [profile]

    session.add(admin)
    session.add(profile)

    return global_data

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)
    env = bootstrap(config_uri)
    settings = env['registry'].settings
    request = env['request']
    engine = engine_from_config(settings, 'sqlalchemy.')
    db_session = scoped_session(sessionmaker())
    db_session.configure(bind=engine)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    data = generate_default_data(db_session)

    db_session.commit()

    if request.search_settings['enabled']:
        request.es.delete_index('profiles')

        for profile in data['profiles']:
            request.es.index(
                'profiles'
                , 'person'
                , profile.__json__(request)
                , id=profile.user.pk
            )

if __name__ == '__main__':
    main()
