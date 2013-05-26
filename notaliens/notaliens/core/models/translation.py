from notaliens.core.models import Base
from sqlalchemy import Column
from sqlalchemy.types import UnicodeText
from sqlalchemy.types import Unicode
from sqlalchemy.types import Integer


class TranslatableMixin(object):
    def get_translations(self, session, language, fields=None):
        parent_type = self.__tablename__

        if not fields:
            fields = getattr(self, '__translatables__', [])

        query = session.query(Translation)
        query = query.filter(Translation.parent_pk == self.pk)
        query = query.filter(Translation.parent_type == parent_type)
        query = query.filter(Translation.language == language)
        query = query.filter(Translation.field.in_(fields))

        translations = query.all()
        translation_dict = {}
        fields_to_create = fields[:]

        for translation in translations:
            translation_dict[translation.field] = translation
            try:
                fields_to_create.remove(translation.field)
            except (ValueError,) as e:
                pass
        # if no translation is found autogenerate one
        for field in fields_to_create:
            translation = Translation(parent_pk=self.pk,
                                      parent_type=parent_type,
                                      language=language,
                                      field=field)
            session.add(translation)
            translation_dict[field] = translation
        return translation_dict


class Translation(Base):
    parent_pk = Column(Integer, nullable=False, autoincrement=False,
                       primary_key=True)
    parent_type = Column(Unicode(24), nullable=False, primary_key=True)
    translation = Column(UnicodeText(), nullable=False, default=u'')
    field = Column(Unicode(24), nullable=False, primary_key=True)
    language = Column(Unicode(4), nullable=False, primary_key=True)

    def __repr__(self):
        return '<Translation: type:"%s",field "%s", lang:%s>' % (
                                                            self.parent_type,
                                                            self.field,
                                                            self.language)

__all__ = ["Translation", "TranslatableMixin"]
