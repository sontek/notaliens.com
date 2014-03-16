from pyramid_deform import CSRFSchema
from deform_bootstrap.widget import ChosenMultipleWidget
from deform_bootstrap.widget import ChosenSingleWidget
from notaliens.people.models import SkillTag
from notaliens.core.models.meta import Country
from notaliens.core.models.meta import Language
from notaliens.core.models.meta import Timezone

import colander
import deform


@colander.deferred
def profile_default(node, kw):
    request = kw.get('request')
    attr = node.name.lower()

    if hasattr(request.context.profile, attr):
        attr_result = getattr(request.context.profile, attr)

        if attr_result:
            return attr_result
        else:
            return ''


@colander.deferred
def language_widget(node, kw):
    """ This will grab the choices to presenter a user in the language dropdown
    of the profile form
    """
    request = kw.get('request')
    choices = []

    languages = request.db_session.query(Language).all()

    for language in languages:
        choices.append((str(language.pk), language.name))

    return ChosenMultipleWidget(values=choices)

@colander.deferred
def language_default(node, kw):
    """ 
        This will return all the languages a user as selected if they have any
    """
    request = kw.get('request')

    if request.context.profile:
        languages = [str(lang.pk) for lang in request.context.profile.languages]

        return tuple(languages)

@colander.deferred
def country_widget(node, kw):
    """ This will return all the countries available for selection in the
    profile form
    """
    choices = [('', '- None -'),]

    request = kw.get('request')

    countries = request.db_session.query(Country).all()

    for country in countries:
        choices.append((str(country.pk), country.name))

    return ChosenSingleWidget(values=choices)

@colander.deferred
def country_default(node, kw):
    """ This will set the user's current selected country if they have one """
    request = kw.get('request')

    if request.context.profile:
        if request.context.profile.country_pk:
            return str(request.context.profile.country.name)


@colander.deferred
def timezone_widget(node, kw):
    """ This will return all the timezones available for selection in the
    profile form
    """
    request = kw.get('request')
    choices = [('', '- None -'),]

    timezones = request.db_session.query(Timezone).all()

    for timezone in timezones:
        choices.append((str(timezone.pk), timezone.name))

    return ChosenSingleWidget(values=choices)


@colander.deferred
def timezone_default(node, kw):
    """ This will set the user's current selected timezone if they have one """
    request = kw.get('request')

    if request.context.profile:
        if request.context.profile.timezone_pk:
            return str(request.context.profile.timezone_pk)


@colander.deferred
def skill_widget(node, kw):
    """ This will grab the choices to present a user in the skills dropdown
    of the profile form
    """
    request = kw.get('request')
    choices = []

    tags = request.db_session.query(SkillTag).order_by(SkillTag.name)

    for tag in tags:
        choices.append((str(tag.pk), tag.name))

    return ChosenMultipleWidget(values=choices)


class ProfileSchema(CSRFSchema):
    """ This is the schema rendered out to the profile form, we define order
    since we are inheriting a few fields from pyramid_signup originally
    """
    username = colander.SchemaNode(colander.String(),
            widget=deform.widget.TextInputWidget(template='readonly/textinput'),
            missing=colander.null,
        )
    email = colander.SchemaNode(colander.String(),
        validator=colander.Email())
    first_name = colander.SchemaNode(
        colander.String(),
        default=profile_default,
    )
    last_name = colander.SchemaNode(
        colander.String(),
        default=profile_default
    )
    city = colander.SchemaNode(colander.String(),
        default=profile_default,
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        missing=None)
    state = colander.SchemaNode(colander.String(),
        default=profile_default,
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        missing=None)
    postal = colander.SchemaNode(colander.String(),
        default=profile_default,
    )
    country = colander.SchemaNode(colander.String(),
        #widget=country_widget,
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        default=country_default, missing=None)
    timezone = colander.SchemaNode(colander.String(),
        widget=timezone_widget,
        missing=None,
        default=timezone_default)
    spoken_Languages = colander.SchemaNode(
        deform.Set(),
        widget=language_widget,
        missing=None,
        default=language_default,
        title='Languages')
    # This is a 140 character one liner about themselves
    one_liner = colander.SchemaNode(colander.String(),
        title="Tagline",
        default=profile_default)
    description = colander.SchemaNode(colander.String(),
        missing=None,
        default=profile_default,
        widget=deform.widget.TextAreaWidget(rows=10, css_class="about-text"))
